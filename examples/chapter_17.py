"""Join exact specialist returns without confusing partial work for completion."""

from orders_investigation.coordination.delegation import (
    EvidenceFact,
    JoinContract,
    Recommendation,
    SpecialistAssignment,
    SpecialistCoordinator,
    SpecialistResult,
)
from orders_investigation.presentation import chapter_presentation

def main() -> None:
    demo = chapter_presentation(17, description=__doc__)
    system = SpecialistCoordinator(
        run_id="orders-run",
        active_plan_version=2,
        current_tasks=frozenset({"confirm_writer", "confirm_orders"}),
        recorded_evidence={
            "writer-17": {"pressure": "falling"},
            "orders-17": {"timeouts": "0.8 percent"},
        },
    )
    assignments = (
        SpecialistAssignment(
            "writer-check", "orders-run", 2, "capacity", "confirm_writer",
            "writer_assessment", ("writer-17",), "recovery", 2,
        ),
        SpecialistAssignment(
            "orders-check", "orders-run", 2, "orders", "confirm_orders",
            "orders_assessment", ("orders-17",), "recovery", 2,
        ),
    )
    for assignment in assignments:
        system.delegate(assignment)
    system.accept_result(
        SpecialistResult(
            "writer-check", "orders-run", 2, "capacity", "confirm_writer",
            "writer_assessment", (EvidenceFact("writer-17", "pressure", "falling"),),
            Recommendation.RECOVERY_SUPPORTED, 1, "assignment_complete",
        )
    )
    contract = JoinContract(
        "recovery",
        "orders-run",
        2,
        ("writer-check", "orders-check"),
        "publish-recovery",
        "publish the supported recovery update",
    )
    demo.scenario(1, "One valid specialist return is still partial")
    partial = system.join(contract)
    demo.fields(
        (
            ("Join outcome", partial.outcome),
            ("Missing assignments", ", ".join(partial.missing_assignments)),
        ),
        style="evidence",
    )
    demo.state("Join contract", False, "one required assignment has not returned")
    system.accept_result(
        SpecialistResult(
            "orders-check", "orders-run", 2, "orders", "confirm_orders",
            "orders_assessment", (EvidenceFact("orders-17", "timeouts", "0.8 percent"),),
            Recommendation.RECOVERY_SUPPORTED, 1, "assignment_complete",
        )
    )
    complete = system.join(contract)
    demo.scenario(2, "Every assigned obligation is returned and checked")
    demo.fields(
        (
            ("Join outcome", complete.outcome),
            (
                "Proposal performs outside effect",
                hasattr(complete.proposal, "effect_result"),
            ),
        )
    )
    demo.decision(True, approved_label="JOIN PROPOSAL READY")
    demo.notice(
        "Specialists return evidence and recommendations, not authority. The "
        "coordinator creates a proposal only after the exact join contract is complete."
    )


if __name__ == "__main__":
    main()
