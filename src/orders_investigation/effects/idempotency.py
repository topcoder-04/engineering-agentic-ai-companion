from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass


class ResponseLost(RuntimeError):
    """The service committed the effect, but the caller did not receive its result."""


class IdempotencyConflict(ValueError):
    """One idempotency key was reused for a different intended effect."""


@dataclass(frozen=True)
class EffectIntent:
    operation: str
    target: str
    content: str

    @property
    def fingerprint(self) -> str:
        canonical = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EffectReceipt:
    effect_id: str
    idempotency_key: str
    status: str
    replayed: bool


class ReportEffectService:
    """Small effect-capable service used to expose idempotency semantics."""

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS report_effects ("
            "idempotency_key TEXT PRIMARY KEY, "
            "intent_fingerprint TEXT NOT NULL, "
            "effect_id TEXT NOT NULL, "
            "status TEXT NOT NULL"
            ")"
        )
        self.connection.commit()

    def apply(
        self,
        intent: EffectIntent,
        *,
        idempotency_key: str,
        lose_response: bool = False,
    ) -> EffectReceipt:
        if not idempotency_key.strip():
            raise ValueError("idempotency_key_required")

        self.connection.execute("BEGIN IMMEDIATE")
        existing = self.connection.execute(
            "SELECT intent_fingerprint, effect_id, status "
            "FROM report_effects WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()

        if existing is not None:
            fingerprint, effect_id, status = existing
            self.connection.commit()
            if fingerprint != intent.fingerprint:
                raise IdempotencyConflict("idempotency_key_reused_for_different_intent")
            return EffectReceipt(effect_id, idempotency_key, status, replayed=True)

        effect_number = self.connection.execute(
            "SELECT COUNT(*) + 1 FROM report_effects"
        ).fetchone()[0]
        effect_id = f"report-effect-{effect_number}"
        self.connection.execute(
            "INSERT INTO report_effects("
            "idempotency_key, intent_fingerprint, effect_id, status"
            ") VALUES (?, ?, ?, ?)",
            (idempotency_key, intent.fingerprint, effect_id, "applied"),
        )
        self.connection.commit()

        receipt = EffectReceipt(effect_id, idempotency_key, "applied", replayed=False)
        if lose_response:
            raise ResponseLost("response_lost_after_effect_commit")
        return receipt

    def lookup(self, idempotency_key: str) -> EffectReceipt | None:
        row = self.connection.execute(
            "SELECT effect_id, status FROM report_effects WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()
        if row is None:
            return None
        return EffectReceipt(row[0], idempotency_key, row[1], replayed=True)

    @property
    def effect_count(self) -> int:
        return self.connection.execute("SELECT COUNT(*) FROM report_effects").fetchone()[0]


def report_update_intent() -> EffectIntent:
    return EffectIntent(
        operation="update_report",
        target="incident_report",
        content=(
            "A deployment-launched migration consumed write capacity and delayed "
            "order completion."
        ),
    )

