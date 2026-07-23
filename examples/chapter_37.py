"""Chapter 37: preserve every independent launch veto."""

from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.journey import (
    orders_conformance_receipt,
    orders_data_boundary,
    orders_delegation,
    orders_lifecycle_ownership,
    run_orders_launch,
)


REFUSED_CANDIDATES = (
    (
        "Insufficient evaluation cases",
        "insufficient_evaluation_cases",
        {"faults": ()},
    ),
    (
        "Safety failure budget exceeded",
        "safety_failure_budget_exceeded",
        {"faults": ("none", "stale_evidence")},
    ),
    (
        "Accountable owner missing",
        "owner_missing",
        {"ownership": orders_lifecycle_ownership(owner="")},
    ),
    (
        "Rollback proof missing",
        "rollback_unproven",
        {
            "receipt": orders_conformance_receipt(
                passed_checks=frozenset(
                    {"trace", "policy", "authority", "placement"}
                )
            )
        },
    ),
    (
        "Caller authority unproven",
        "caller_authority_unproven",
        {"delegation": orders_delegation(action="refund.issue")},
    ),
    (
        "Data boundary unproven",
        "data_boundary_unproven",
        {"boundary": orders_data_boundary(region="us-east-1")},
    ),
)



def main() -> None:
    demo = chapter_presentation(37, description=__doc__)

    allowed = run_orders_launch()
    refused = tuple(
        (label, expected_reason, run_orders_launch(**launch_inputs))
        for label, expected_reason, launch_inputs in REFUSED_CANDIDATES
    )

    demo.section("The system we built")
    demo.numbered_map(
        (
            (
                "Bounded investigation",
                "completion · tasks · evidence · graph execution",
            ),
            (
                "Reliable effects",
                "idempotency · unknown outcomes · reconciliation · isolation",
            ),
            (
                "Durable operation",
                "recovery · ownership · authorization · policy",
            ),
            (
                "Production judgment",
                "observability · evaluation · release · fleet learning",
            ),
            (
                "Governed evolution",
                "identity · capability · authority · placement · launch risk",
            ),
        )
    )

    demo.scenario(1, "Every launch obligation is proven")
    demo.fields(
        (
            ("Evaluation cases", allowed.evidence.cases),
            ("Safety failures", allowed.evidence.safety_failures),
            ("Owner assigned", "YES" if allowed.evidence.owner_present else "NO"),
            (
                "Rollback proven",
                "YES" if allowed.evidence.rollback_proven else "NO",
            ),
            (
                "Caller authority",
                "PROVEN" if allowed.evidence.caller_authority_proven else "UNPROVEN",
            ),
            (
                "Data boundary",
                "PROVEN" if allowed.evidence.data_boundary_proven else "UNPROVEN",
            ),
        ),
        style="evidence",
    )
    demo.section("Connected launch path")
    demo.path(
        (
            "identified",
            "capability admitted",
            "scaffolded",
            "conformance bound",
            "owned",
            "compatibility checked",
            "caller authorized",
            "placed",
            "variation evaluated",
            "risk approved",
            "effect executed once",
        )
    )
    demo.decision(allowed.decision[0], approved_label="LAUNCH APPROVED")
    demo.execution(
        allowed.execution is not None,
        "Orders report written once",
    )
    if allowed.execution is not None:
        demo.path(
            tuple(
                step.kind
                for step in allowed.execution.registered.journey.steps
            )
        )

    demo.scenario(2, "Remove one proof at a time")
    for label, expected_reason, result in refused:
        if result.decision != (False, (expected_reason,)):
            raise RuntimeError(
                f"{label} produced an unexpected launch decision: {result.decision}"
            )
        actual_reasons = result.decision[1]
        reason = actual_reasons[0] if len(actual_reasons) == 1 else repr(actual_reasons)
        detail = f"{reason} · NOT EXECUTED"
        demo.result_row(
            label,
            accepted=False,
            outcome="LAUNCH REFUSED",
            detail=detail,
        )

    demo.notice(
        "Each candidate removes one proof, receives one exact veto, and stops "
        "before the effect. No stronger score compensates for a missing boundary."
    )


if __name__ == "__main__":
    main()
