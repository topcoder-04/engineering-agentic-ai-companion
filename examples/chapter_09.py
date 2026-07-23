"""Run the post-dispatch timeout and reconciliation path."""

import asyncio
import sqlite3

from orders_investigation.effects.idempotency import (
    ReportEffectService,
    report_update_intent,
)
from orders_investigation.effects.reconciliation import (
    EffectOutcome,
    dispatch_with_timeout,
    reconcile,
)
from orders_investigation.presentation import chapter_presentation


async def scenario(demo) -> None:
    service = ReportEffectService(sqlite3.connect(":memory:"))
    dispatched = await dispatch_with_timeout(
        service,
        report_update_intent(),
        idempotency_key="report-update:run-1042:1",
        timeout_seconds=0.001,
        service_delay_seconds=0.01,
    )
    demo.scenario(1, "The local wait ends after dispatch")
    demo.fields(
        (
            ("Dispatched", dispatched.attempt.dispatched),
            ("Local wait", dispatched.attempt.wait_outcome),
            ("Effect outcome", dispatched.attempt.effect_outcome.value),
        ),
        style="evidence",
    )
    demo.decision(
        False,
        refused_label="OUTCOME NOT YET KNOWN",
        reason=dispatched.attempt.effect_outcome.value,
    )
    assert dispatched.outside_task is not None
    await dispatched.outside_task
    recovered = reconcile(service, dispatched.attempt)
    demo.scenario(2, "Reconciliation asks the effect service what committed")
    demo.fields(
        (
            ("Effects applied", service.effect_count),
            ("Reconciled outcome", recovered.effect_outcome.value),
            ("Effect id", recovered.reconciled_receipt.effect_id),
        )
    )
    demo.execution(service.effect_count == 1, "outside effect resolved as succeeded")
    assert recovered.effect_outcome is EffectOutcome.SUCCEEDED
    demo.notice(
        "The timeout ends only the caller's wait. The effect remains unknown "
        "until reconciliation observes the authoritative service state."
    )


def main() -> None:
    demo = chapter_presentation(9, description=__doc__)
    asyncio.run(scenario(demo))


if __name__ == "__main__":
    main()
