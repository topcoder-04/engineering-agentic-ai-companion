from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from enum import StrEnum


class PlanRefused(ValueError):
    pass


class CommitmentStatus(StrEnum):
    SUCCEEDED = "succeeded"
    READY = "ready"
    WAITING = "waiting"


@dataclass(frozen=True)
class EvidenceReference:
    key: str
    value: str


@dataclass(frozen=True)
class Commitment:
    task_id: str
    status: CommitmentStatus


@dataclass(frozen=True)
class Plan:
    run_id: str
    version: int
    question: str
    evidence_boundary: tuple[EvidenceReference, ...]
    commitments: tuple[Commitment, ...]
    supersedes_version: int | None = None


@dataclass(frozen=True)
class PlanReplacement:
    previous_version: int
    current_version: int
    changed_evidence: tuple[str, ...]
    preserved_succeeded: tuple[str, ...]
    superseded_future: tuple[str, ...]
    added_future: tuple[str, ...]


def changed_evidence(plan: Plan, recorded: dict[str, str]) -> tuple[str, ...]:
    return tuple(
        item.key
        for item in plan.evidence_boundary
        if recorded.get(item.key) != item.value
    )


class PlanStore:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS plans ("
            "run_id TEXT NOT NULL, version INTEGER NOT NULL, active INTEGER NOT NULL, "
            "body TEXT NOT NULL, PRIMARY KEY(run_id, version))"
        )

    @staticmethod
    def _encode(plan: Plan) -> str:
        return json.dumps(asdict(plan), sort_keys=True)

    @staticmethod
    def _decode(raw: str) -> Plan:
        body = json.loads(raw)
        return Plan(
            run_id=body["run_id"],
            version=body["version"],
            question=body["question"],
            evidence_boundary=tuple(
                EvidenceReference(**item) for item in body["evidence_boundary"]
            ),
            commitments=tuple(
                Commitment(item["task_id"], CommitmentStatus(item["status"]))
                for item in body["commitments"]
            ),
            supersedes_version=body["supersedes_version"],
        )

    def create(self, plan: Plan, recorded: dict[str, str]) -> None:
        if plan.version != 1 or plan.supersedes_version is not None:
            raise PlanRefused("initial_plan_version_invalid")
        self._validate_boundary(plan, recorded)
        self.connection.execute(
            "INSERT INTO plans(run_id, version, active, body) VALUES(?, ?, 1, ?)",
            (plan.run_id, plan.version, self._encode(plan)),
        )
        self.connection.commit()

    def active(self, run_id: str) -> Plan:
        row = self.connection.execute(
            "SELECT body FROM plans WHERE run_id = ? AND active = 1",
            (run_id,),
        ).fetchone()
        if row is None:
            raise KeyError(run_id)
        return self._decode(row[0])

    def require_current(self, run_id: str, version: int) -> Plan:
        plan = self.active(run_id)
        if plan.version != version:
            raise PlanRefused("plan_version_not_active")
        return plan

    @staticmethod
    def _validate_boundary(plan: Plan, recorded: dict[str, str]) -> None:
        for item in plan.evidence_boundary:
            if recorded.get(item.key) != item.value:
                raise PlanRefused(f"evidence_boundary_mismatch:{item.key}")

    def replace(
        self,
        replacement: Plan,
        recorded: dict[str, str],
        *,
        fail_before_commit: bool = False,
    ) -> PlanReplacement:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            current = self.active(replacement.run_id)
            if replacement.supersedes_version != current.version:
                raise PlanRefused("superseded_version_mismatch")
            if replacement.version != current.version + 1:
                raise PlanRefused("replacement_version_invalid")
            changed = changed_evidence(current, recorded)
            if not changed:
                raise PlanRefused("evidence_did_not_change")
            self._validate_boundary(replacement, recorded)

            old_succeeded = {
                item.task_id for item in current.commitments
                if item.status == CommitmentStatus.SUCCEEDED
            }
            new_succeeded = {
                item.task_id for item in replacement.commitments
                if item.status == CommitmentStatus.SUCCEEDED
            }
            if not old_succeeded <= new_succeeded:
                raise PlanRefused("succeeded_commitment_removed")

            old_future = {
                item.task_id for item in current.commitments
                if item.status != CommitmentStatus.SUCCEEDED
            }
            new_future = {
                item.task_id for item in replacement.commitments
                if item.status != CommitmentStatus.SUCCEEDED
            }
            self.connection.execute(
                "UPDATE plans SET active = 0 WHERE run_id = ? AND version = ?",
                (current.run_id, current.version),
            )
            self.connection.execute(
                "INSERT INTO plans(run_id, version, active, body) VALUES(?, ?, 1, ?)",
                (replacement.run_id, replacement.version, self._encode(replacement)),
            )
            if fail_before_commit:
                raise RuntimeError("injected_before_plan_commit")
            self.connection.commit()
            return PlanReplacement(
                previous_version=current.version,
                current_version=replacement.version,
                changed_evidence=changed,
                preserved_succeeded=tuple(sorted(old_succeeded)),
                superseded_future=tuple(sorted(old_future - new_future)),
                added_future=tuple(sorted(new_future - old_future)),
            )
        except Exception:
            self.connection.rollback()
            raise
