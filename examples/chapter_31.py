"""Chapter 31: preserve caller-bound delegated authority."""
from orders_investigation.runtime.journey import (
    orders_caller,
    orders_delegation,
    run_delegated_orders_investigation,
)
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(31, description=__doc__)
    caller = orders_caller()
    delegation = orders_delegation()
    accepted = run_delegated_orders_investigation(caller, delegation)
    demo.scenario(1, "Caller and delegation remain bound through execution")
    demo.fields(
        (
            ("Caller", caller.subject),
            ("Tenant", caller.tenant_id),
            ("Delegated action", ", ".join(sorted(delegation.allowed_actions))),
            ("Journey completed", accepted.journey.completed),
        ),
        style="evidence",
    )
    demo.decision(True, approved_label="CALLER AUTHORITY PROVEN")
    demo.scenario(2, "The service cannot widen the caller's action")
    try:
        run_delegated_orders_investigation(
            caller, delegation, action="refund.issue"
        )
    except ValueError as exc:
        demo.decision(False, refused_label="UNDELEGATED ACTION REFUSED", reason=str(exc))
    demo.notice(
        "The agent's service identity does not replace the caller. Tenant, "
        "caller, agent, action, audience, and expiry stay connected in one proof."
    )


if __name__ == "__main__":
    main()
