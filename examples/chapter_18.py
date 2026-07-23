"""Persist an exact approval intent and correlate the returning signal."""

import sqlite3
from datetime import datetime, timedelta, timezone

from orders_investigation.governance.approval import (
    ApprovalDecision,
    ApprovalIntent,
    ApprovalRefused,
    ApprovalRequest,
    ApprovalSignal,
    ApprovalStore,
)
from orders_investigation.presentation import chapter_presentation

def main() -> None:
    demo = chapter_presentation(18, description=__doc__)
    now = datetime(2026, 7, 21, 16, 0, tzinfo=timezone.utc)
    intent = ApprovalIntent(
        "publish_recovery_update",
        "orders-incident-report",
        "Order completion recovered.",
        ("writer-17", "orders-17"),
    )
    request = ApprovalRequest(
        "approval-orders-recovery",
        "orders-run",
        2,
        "publish-recovery",
        intent,
        now,
        now + timedelta(minutes=30),
    )
    store = ApprovalStore(sqlite3.connect(":memory:"))
    waiting = store.create(request)
    demo.scenario(1, "The exact intent is stored while the run waits")
    demo.fields(
        (
            ("Approval status", waiting.status.value),
            ("Intent digest", intent.digest[:12] + "…"),
            ("Expires", request.expires_at.isoformat()),
        ),
        style="evidence",
    )
    try:
        store.deliver(
            ApprovalSignal(
                "wrong-intent",
                request.approval_id,
                "0" * 64,
                ApprovalDecision.APPROVE,
                now + timedelta(minutes=1),
            )
        )
    except ApprovalRefused as error:
        demo.decision(False, refused_label="UNBOUND APPROVAL REFUSED", reason=str(error))
    receipt = store.deliver(
        ApprovalSignal(
            "exact-signal",
            request.approval_id,
            intent.digest,
            ApprovalDecision.APPROVE,
            now + timedelta(minutes=2),
        )
    )
    demo.scenario(2, "A correlated signal authorizes the stored intent")
    demo.fields(
        (
            ("Approval status", receipt.status.value),
            ("Duplicate", receipt.duplicate),
            ("Signal intent", intent.digest[:12] + "…"),
        )
    )
    demo.decision(True, approved_label="EXACT INTENT APPROVED")
    demo.notice(
        "The returning signal must match the approval id, intent digest, and "
        "expiry. A bare yes cannot authorize changed content."
    )


if __name__ == "__main__":
    main()
