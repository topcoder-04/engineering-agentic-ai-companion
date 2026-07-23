import asyncio
import sqlite3

from orders_investigation.effects.idempotency import ReportEffectService, report_update_intent
from orders_investigation.effects.reconciliation import (
    EffectAttemptStore,
    EffectOutcome,
    dispatch_with_timeout,
    failure_before_dispatch,
    reconcile,
)


def test_timeout_after_dispatch_remains_unknown_until_reconciliation(tmp_path):
    async def scenario():
        connection = sqlite3.connect(tmp_path / "lifecycle.sqlite")
        service = ReportEffectService(connection)
        dispatched = await dispatch_with_timeout(
            service,
            report_update_intent(),
            idempotency_key="report-update:run-1042:1",
            timeout_seconds=0.001,
            service_delay_seconds=0.01,
        )
        assert dispatched.attempt.dispatched
        assert dispatched.attempt.effect_outcome == EffectOutcome.UNKNOWN
        assert dispatched.attempt.wait_outcome == "timeout_local_wait_cancelled"
        assert dispatched.outside_task is not None

        EffectAttemptStore(connection).save(dispatched.attempt)

        await dispatched.outside_task
        assert service.effect_count == 1
        connection.close()

        replacement = sqlite3.connect(tmp_path / "lifecycle.sqlite")
        restored_attempt = EffectAttemptStore(replacement).load(
            "report-update:run-1042:1"
        )
        assert restored_attempt.effect_outcome == EffectOutcome.UNKNOWN
        recovered = reconcile(ReportEffectService(replacement), restored_attempt)
        EffectAttemptStore(replacement).save(recovered)
        assert recovered.effect_outcome == EffectOutcome.SUCCEEDED
        assert recovered.reconciled_receipt is not None
        assert recovered.reconciled_receipt.effect_id == "report-effect-1"
        replacement.close()

    asyncio.run(scenario())


def test_local_timeout_does_not_cancel_the_outside_effect(tmp_path):
    async def scenario():
        connection = sqlite3.connect(tmp_path / "shielded.sqlite")
        service = ReportEffectService(connection)
        dispatched = await dispatch_with_timeout(
            service,
            report_update_intent(),
            idempotency_key="report-update:run-1042:1",
            timeout_seconds=0.001,
            service_delay_seconds=0.01,
        )
        assert dispatched.outside_task is not None
        assert not dispatched.outside_task.cancelled()
        await dispatched.outside_task
        assert service.effect_count == 1
        connection.close()

    asyncio.run(scenario())


def test_failure_before_dispatch_is_known_not_to_have_reached_the_service():
    attempt = failure_before_dispatch("report-update:run-1042:1")
    assert not attempt.dispatched
    assert attempt.effect_outcome == EffectOutcome.NOT_DISPATCHED
