from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum


class ApprovalRefused(ValueError):
    pass


class ApprovalDecision(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"


class ApprovalStatus(StrEnum):
    WAITING = "waiting"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass(frozen=True)
class ApprovalIntent:
    operation: str
    target: str
    content: str
    supporting_evidence: tuple[str, ...]

    @property
    def digest(self) -> str:
        body = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(body.encode()).hexdigest()


@dataclass(frozen=True)
class ApprovalRequest:
    approval_id: str
    run_id: str
    plan_version: int
    proposal_id: str
    intent: ApprovalIntent
    requested_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class ApprovalSignal:
    signal_id: str
    approval_id: str
    intent_digest: str
    decision: ApprovalDecision
    observed_at: datetime


@dataclass(frozen=True)
class ApprovalRecord:
    request: ApprovalRequest
    status: ApprovalStatus
    decision_signal_id: str | None


@dataclass(frozen=True)
class ApprovalReceipt:
    approval_id: str
    intent_digest: str
    status: ApprovalStatus
    duplicate: bool


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ApprovalRefused("approval_time_requires_timezone")
    return value.astimezone(timezone.utc)


class ApprovalStore:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS approvals ("
            "approval_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, "
            "plan_version INTEGER NOT NULL, proposal_id TEXT NOT NULL, "
            "intent_json TEXT NOT NULL, intent_digest TEXT NOT NULL, "
            "requested_at TEXT NOT NULL, expires_at TEXT NOT NULL, "
            "status TEXT NOT NULL, decision_signal_id TEXT)"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS approval_signals ("
            "signal_id TEXT PRIMARY KEY, approval_id TEXT NOT NULL, "
            "signal_json TEXT NOT NULL)"
        )

    @staticmethod
    def _intent_json(intent: ApprovalIntent) -> str:
        return json.dumps(asdict(intent), sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _signal_json(signal: ApprovalSignal) -> str:
        body = {
            **asdict(signal),
            "decision": signal.decision.value,
            "observed_at": _utc(signal.observed_at).isoformat(),
        }
        return json.dumps(body, sort_keys=True, separators=(",", ":"))

    def create(self, request: ApprovalRequest) -> ApprovalRecord:
        requested_at = _utc(request.requested_at)
        expires_at = _utc(request.expires_at)
        if expires_at <= requested_at:
            raise ApprovalRefused("approval_expiry_invalid")
        try:
            self.connection.execute(
                "INSERT INTO approvals(approval_id, run_id, plan_version, proposal_id, "
                "intent_json, intent_digest, requested_at, expires_at, status, "
                "decision_signal_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)",
                (
                    request.approval_id,
                    request.run_id,
                    request.plan_version,
                    request.proposal_id,
                    self._intent_json(request.intent),
                    request.intent.digest,
                    requested_at.isoformat(),
                    expires_at.isoformat(),
                    ApprovalStatus.WAITING.value,
                ),
            )
            self.connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ApprovalRefused("approval_request_already_exists") from exc
        return self.load(request.approval_id)

    def load(self, approval_id: str) -> ApprovalRecord:
        row = self.connection.execute(
            "SELECT run_id, plan_version, proposal_id, intent_json, intent_digest, "
            "requested_at, expires_at, status, decision_signal_id "
            "FROM approvals WHERE approval_id = ?",
            (approval_id,),
        ).fetchone()
        if row is None:
            raise KeyError(approval_id)
        intent_body = json.loads(row[3])
        request = ApprovalRequest(
            approval_id=approval_id,
            run_id=row[0],
            plan_version=row[1],
            proposal_id=row[2],
            intent=ApprovalIntent(
                operation=intent_body["operation"],
                target=intent_body["target"],
                content=intent_body["content"],
                supporting_evidence=tuple(intent_body["supporting_evidence"]),
            ),
            requested_at=datetime.fromisoformat(row[5]),
            expires_at=datetime.fromisoformat(row[6]),
        )
        if request.intent.digest != row[4]:
            raise ApprovalRefused("approval_intent_record_mismatch")
        return ApprovalRecord(request, ApprovalStatus(row[7]), row[8])

    def deliver(self, signal: ApprovalSignal) -> ApprovalReceipt:
        signal_json = self._signal_json(signal)
        existing_signal = self.connection.execute(
            "SELECT approval_id, signal_json FROM approval_signals WHERE signal_id = ?",
            (signal.signal_id,),
        ).fetchone()
        if existing_signal is not None:
            if existing_signal != (signal.approval_id, signal_json):
                raise ApprovalRefused("approval_signal_conflict")
            record = self.load(signal.approval_id)
            return ApprovalReceipt(
                signal.approval_id,
                record.request.intent.digest,
                record.status,
                True,
            )

        try:
            record = self.load(signal.approval_id)
        except KeyError as exc:
            raise ApprovalRefused("approval_request_unknown") from exc
        if record.status != ApprovalStatus.WAITING:
            raise ApprovalRefused("approval_already_decided")
        if signal.intent_digest != record.request.intent.digest:
            raise ApprovalRefused("approval_intent_mismatch")

        observed_at = _utc(signal.observed_at)
        if observed_at > record.request.expires_at:
            self.connection.execute(
                "UPDATE approvals SET status = ? WHERE approval_id = ?",
                (ApprovalStatus.EXPIRED.value, signal.approval_id),
            )
            self.connection.commit()
            raise ApprovalRefused("approval_expired")

        status = (
            ApprovalStatus.APPROVED
            if signal.decision == ApprovalDecision.APPROVE
            else ApprovalStatus.REJECTED
        )
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            self.connection.execute(
                "INSERT INTO approval_signals(signal_id, approval_id, signal_json) "
                "VALUES(?, ?, ?)",
                (signal.signal_id, signal.approval_id, signal_json),
            )
            transition = self.connection.execute(
                "UPDATE approvals SET status = ?, decision_signal_id = ? "
                "WHERE approval_id = ? AND status = ?",
                (
                    status.value,
                    signal.signal_id,
                    signal.approval_id,
                    ApprovalStatus.WAITING.value,
                ),
            )
            if transition.rowcount != 1:
                raise ApprovalRefused("approval_transition_lost")
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        return ApprovalReceipt(
            signal.approval_id,
            record.request.intent.digest,
            status,
            False,
        )
