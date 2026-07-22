from __future__ import annotations

import asyncio
import sqlite3
from dataclasses import dataclass, replace
from enum import StrEnum

from orders_investigation.effects.idempotency import EffectIntent, EffectReceipt, ReportEffectService


class EffectOutcome(StrEnum):
    NOT_DISPATCHED = "not_dispatched"
    UNKNOWN = "unknown"
    SUCCEEDED = "succeeded"


@dataclass(frozen=True)
class EffectAttempt:
    idempotency_key: str
    dispatched: bool
    wait_outcome: str
    effect_outcome: EffectOutcome
    reconciled_receipt: EffectReceipt | None = None


@dataclass(frozen=True)
class TimedDispatch:
    attempt: EffectAttempt
    outside_task: asyncio.Task[EffectReceipt] | None


class EffectAttemptStore:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS effect_attempts ("
            "idempotency_key TEXT PRIMARY KEY, "
            "dispatched INTEGER NOT NULL, "
            "wait_outcome TEXT NOT NULL, "
            "effect_outcome TEXT NOT NULL, "
            "effect_id TEXT, "
            "effect_status TEXT"
            ")"
        )
        self.connection.commit()

    def save(self, attempt: EffectAttempt) -> None:
        receipt = attempt.reconciled_receipt
        self.connection.execute(
            "INSERT INTO effect_attempts("
            "idempotency_key, dispatched, wait_outcome, effect_outcome, "
            "effect_id, effect_status"
            ") VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(idempotency_key) DO UPDATE SET "
            "dispatched=excluded.dispatched, "
            "wait_outcome=excluded.wait_outcome, "
            "effect_outcome=excluded.effect_outcome, "
            "effect_id=excluded.effect_id, "
            "effect_status=excluded.effect_status",
            (
                attempt.idempotency_key,
                int(attempt.dispatched),
                attempt.wait_outcome,
                attempt.effect_outcome.value,
                receipt.effect_id if receipt else None,
                receipt.status if receipt else None,
            ),
        )
        self.connection.commit()

    def load(self, idempotency_key: str) -> EffectAttempt:
        row = self.connection.execute(
            "SELECT dispatched, wait_outcome, effect_outcome, effect_id, effect_status "
            "FROM effect_attempts WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()
        if row is None:
            raise KeyError(idempotency_key)
        dispatched, wait_outcome, effect_outcome, effect_id, effect_status = row
        receipt = None
        if effect_id is not None:
            receipt = EffectReceipt(
                effect_id,
                idempotency_key,
                effect_status,
                replayed=True,
            )
        return EffectAttempt(
            idempotency_key=idempotency_key,
            dispatched=bool(dispatched),
            wait_outcome=wait_outcome,
            effect_outcome=EffectOutcome(effect_outcome),
            reconciled_receipt=receipt,
        )


async def dispatch_with_timeout(
    service: ReportEffectService,
    intent: EffectIntent,
    *,
    idempotency_key: str,
    timeout_seconds: float,
    service_delay_seconds: float,
) -> TimedDispatch:
    async def outside_request() -> EffectReceipt:
        await asyncio.sleep(service_delay_seconds)
        return service.apply(intent, idempotency_key=idempotency_key)

    outside_task = asyncio.create_task(outside_request())
    try:
        receipt = await asyncio.wait_for(
            asyncio.shield(outside_task),
            timeout=timeout_seconds,
        )
    except TimeoutError:
        return TimedDispatch(
            EffectAttempt(
                idempotency_key=idempotency_key,
                dispatched=True,
                wait_outcome="timeout_local_wait_cancelled",
                effect_outcome=EffectOutcome.UNKNOWN,
            ),
            outside_task,
        )
    return TimedDispatch(
        EffectAttempt(
            idempotency_key=idempotency_key,
            dispatched=True,
            wait_outcome="response_received",
            effect_outcome=EffectOutcome.SUCCEEDED,
            reconciled_receipt=receipt,
        ),
        outside_task,
    )


def failure_before_dispatch(idempotency_key: str) -> EffectAttempt:
    return EffectAttempt(
        idempotency_key=idempotency_key,
        dispatched=False,
        wait_outcome="failed_before_dispatch",
        effect_outcome=EffectOutcome.NOT_DISPATCHED,
    )


def reconcile(
    service: ReportEffectService,
    attempt: EffectAttempt,
) -> EffectAttempt:
    receipt = service.lookup(attempt.idempotency_key)
    if receipt is None:
        return attempt
    return replace(
        attempt,
        effect_outcome=EffectOutcome.SUCCEEDED,
        reconciled_receipt=receipt,
    )

