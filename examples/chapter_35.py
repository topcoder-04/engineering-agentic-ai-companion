"""Chapter 35: ownership cannot waive a non-waivable boundary."""

from datetime import datetime, timedelta, timezone

from orders_investigation.platform.lifecycle import ExceptionGrant, validate_exception
from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.journey import (
    orders_lifecycle_ownership,
    run_owned_orders_investigation,
)


def main() -> None:
    demo = chapter_presentation(35, description=__doc__)
    ownership = orders_lifecycle_ownership()
    accepted = run_owned_orders_investigation(ownership)
    now = datetime(2026, 7, 21, tzinfo=timezone.utc)
    grant = ExceptionGrant(
        "residency-exception",
        "security",
        "residency",
        now + timedelta(days=1),
        ("manual-review",),
        waivable=False,
    )
    exception_allowed = validate_exception(grant, "residency", now)
    demo.scenario(1, "Launch names its durable operating owners")
    demo.fields(
        (
            ("Operator", ownership.owner),
            ("Runbook", ownership.runbook),
            ("Rollback owner", ownership.rollback_owner),
            ("Journey completed", accepted.registered.journey.completed),
        ),
        style="evidence",
    )
    demo.result_row(
        "Residency exception",
        accepted=exception_allowed,
        outcome="ALLOWED" if exception_allowed else "NON-WAIVABLE",
        detail="ownership cannot waive a hard data boundary",
    )
    demo.scenario(2, "A conformant but ownerless candidate is refused")
    try:
        run_owned_orders_investigation(orders_lifecycle_ownership(owner=""))
    except ValueError as exc:
        demo.decision(False, refused_label="OWNERSHIP REFUSED", reason=str(exc))
    demo.notice(
        "Ownership makes repair and rollback accountable. It may manage an "
        "expiring exception, but it cannot waive a non-waivable boundary."
    )


if __name__ == "__main__":
    main()
