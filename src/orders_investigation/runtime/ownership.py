from __future__ import annotations

import sqlite3
from dataclasses import dataclass


class ClaimUnavailable(ValueError):
    pass


class StaleCompletion(ValueError):
    pass


class IntakeDeferred(ValueError):
    pass


@dataclass(frozen=True)
class TaskClaim:
    task_id: str
    worker_id: str
    lease_until: float
    fencing_token: int


class ClaimStore:
    def __init__(self, connection: sqlite3.Connection, *, max_in_flight: int = 2):
        self.connection = connection
        self.max_in_flight = max_in_flight
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS task_claims ("
            "task_id TEXT PRIMARY KEY, status TEXT NOT NULL, worker_id TEXT, "
            "lease_until REAL, fencing_token INTEGER NOT NULL DEFAULT 0, result TEXT)"
        )

    def add_ready(self, task_id: str) -> None:
        self.connection.execute(
            "INSERT OR IGNORE INTO task_claims(task_id, status) VALUES(?, 'ready')",
            (task_id,),
        )
        self.connection.commit()

    def claim(
        self,
        task_id: str,
        worker_id: str,
        *,
        now: float,
        lease_seconds: float,
    ) -> TaskClaim:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            active = self.connection.execute(
                "SELECT COUNT(*) FROM task_claims "
                "WHERE status = 'claimed' AND lease_until > ?",
                (now,),
            ).fetchone()[0]
            if active >= self.max_in_flight:
                raise IntakeDeferred("in_flight_limit_reached")

            row = self.connection.execute(
                "SELECT status, worker_id, lease_until, fencing_token "
                "FROM task_claims WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise KeyError(task_id)
            status, _, lease_until, token = row
            if status == "succeeded":
                raise ClaimUnavailable("task_already_succeeded")
            if status == "claimed" and lease_until is not None and lease_until > now:
                raise ClaimUnavailable("lease_active")

            claim = TaskClaim(task_id, worker_id, now + lease_seconds, token + 1)
            self.connection.execute(
                "UPDATE task_claims SET status = 'claimed', worker_id = ?, "
                "lease_until = ?, fencing_token = ? WHERE task_id = ?",
                (claim.worker_id, claim.lease_until, claim.fencing_token, task_id),
            )
            self.connection.commit()
            return claim
        except Exception:
            self.connection.rollback()
            raise

    def commit(self, claim: TaskClaim, result: str, *, now: float) -> None:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT status, worker_id, lease_until, fencing_token "
                "FROM task_claims WHERE task_id = ?",
                (claim.task_id,),
            ).fetchone()
            if row is None:
                raise KeyError(claim.task_id)
            status, worker_id, lease_until, token = row
            if (
                status != "claimed"
                or worker_id != claim.worker_id
                or token != claim.fencing_token
                or lease_until is None
                or lease_until <= now
            ):
                raise StaleCompletion("claim_no_longer_current")
            self.connection.execute(
                "UPDATE task_claims SET status = 'succeeded', result = ? "
                "WHERE task_id = ? AND fencing_token = ?",
                (result, claim.task_id, claim.fencing_token),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def state(self, task_id: str) -> tuple[str, str | None, int, str | None]:
        row = self.connection.execute(
            "SELECT status, worker_id, fencing_token, result "
            "FROM task_claims WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            raise KeyError(task_id)
        return row
