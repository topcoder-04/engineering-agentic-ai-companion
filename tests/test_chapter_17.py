import pytest

from orders_investigation.coordination.delegation import (
    CoordinationRefused,
    EvidenceFact,
    JoinContract,
    Recommendation,
    SpecialistAssignment,
    SpecialistCoordinator,
    SpecialistResult,
)


def coordinator():
    return SpecialistCoordinator(
        run_id="run-1077",
        active_plan_version=2,
        current_tasks=frozenset({"confirm_writer_recovery", "confirm_order_recovery"}),
        recorded_evidence={
            "writer-recovery-17": {
                "writer_pressure": "43 percent",
                "trend": "falling",
            },
            "orders-recovery-17": {
                "completion_timeout_rate": "0.8 percent",
                "trend": "falling",
            },
        },
    )


def assignments():
    return (
        SpecialistAssignment(
            assignment_id="writer-check",
            run_id="run-1077",
            plan_version=2,
            specialist_id="capacity-specialist",
            task_id="confirm_writer_recovery",
            result_kind="writer_recovery_assessment",
            allowed_evidence_ids=("writer-recovery-17",),
            join_id="recovery-join",
            max_turns=2,
        ),
        SpecialistAssignment(
            assignment_id="orders-check",
            run_id="run-1077",
            plan_version=2,
            specialist_id="orders-specialist",
            task_id="confirm_order_recovery",
            result_kind="orders_recovery_assessment",
            allowed_evidence_ids=("orders-recovery-17",),
            join_id="recovery-join",
            max_turns=2,
        ),
    )


def results(*, orders_recommendation=Recommendation.RECOVERY_SUPPORTED):
    return (
        SpecialistResult(
            assignment_id="writer-check",
            run_id="run-1077",
            plan_version=2,
            specialist_id="capacity-specialist",
            task_id="confirm_writer_recovery",
            result_kind="writer_recovery_assessment",
            facts=(EvidenceFact("writer-recovery-17", "writer_pressure", "43 percent"),),
            recommendation=Recommendation.RECOVERY_SUPPORTED,
            turns_used=1,
            stop_reason="assignment_complete",
        ),
        SpecialistResult(
            assignment_id="orders-check",
            run_id="run-1077",
            plan_version=2,
            specialist_id="orders-specialist",
            task_id="confirm_order_recovery",
            result_kind="orders_recovery_assessment",
            facts=(EvidenceFact(
                "orders-recovery-17",
                "completion_timeout_rate",
                "0.8 percent",
            ),),
            recommendation=orders_recommendation,
            turns_used=1,
            stop_reason="assignment_complete",
        ),
    )


def join_contract():
    return JoinContract(
        join_id="recovery-join",
        run_id="run-1077",
        plan_version=2,
        required_assignments=("writer-check", "orders-check"),
        proposal_id="prepare-recovery-update",
        proposed_intent="publish the recovery update and mark customer impact resolved",
    )


def test_exact_specialist_returns_join_into_one_proposal():
    system = coordinator()
    for assignment in assignments():
        system.delegate(assignment)
    for result in results():
        system.accept_result(result)

    joined = system.join(join_contract())

    assert joined.outcome == "joined"
    assert joined.proposal is not None
    assert joined.proposal.supporting_evidence == (
        "writer-recovery-17",
        "orders-recovery-17",
    )


def test_join_remains_incomplete_when_one_assignment_has_not_returned():
    system = coordinator()
    for assignment in assignments():
        system.delegate(assignment)
    system.accept_result(results()[0])

    joined = system.join(join_contract())

    assert joined.outcome == "incomplete"
    assert joined.missing_assignments == ("orders-check",)
    assert joined.proposal is None


def test_return_from_the_wrong_specialist_is_refused():
    system = coordinator()
    system.delegate(assignments()[0])
    mismatched = SpecialistResult(
        **{**results()[0].__dict__, "specialist_id": "orders-specialist"}
    )

    with pytest.raises(CoordinationRefused, match="result_contract_mismatch"):
        system.accept_result(mismatched)


def test_return_cannot_invent_or_change_recorded_evidence():
    system = coordinator()
    system.delegate(assignments()[0])
    unsupported = SpecialistResult(
        **{
            **results()[0].__dict__,
            "facts": (
                EvidenceFact("writer-recovery-17", "writer_pressure", "20 percent"),
            ),
        }
    )

    with pytest.raises(
        CoordinationRefused,
        match="result_not_supported_by_recorded_evidence",
    ):
        system.accept_result(unsupported)


def test_specialist_return_cannot_exceed_its_turn_limit():
    system = coordinator()
    system.delegate(assignments()[0])
    over_budget = SpecialistResult(
        **{**results()[0].__dict__, "turns_used": 3}
    )

    with pytest.raises(CoordinationRefused, match="result_turn_budget_invalid"):
        system.accept_result(over_budget)


def test_stale_plan_cannot_delegate_or_join_current_work():
    system = coordinator()
    stale_assignment = SpecialistAssignment(
        **{**assignments()[0].__dict__, "plan_version": 1}
    )
    with pytest.raises(CoordinationRefused, match="assignment_plan_not_active"):
        system.delegate(stale_assignment)

    stale_join = JoinContract(**{**join_contract().__dict__, "plan_version": 1})
    with pytest.raises(CoordinationRefused, match="join_plan_not_active"):
        system.join(stale_join)


def test_a_negative_specialist_return_blocks_the_joined_proposal():
    system = coordinator()
    for assignment in assignments():
        system.delegate(assignment)
    for result in results(orders_recommendation=Recommendation.UNCERTAIN):
        system.accept_result(result)

    joined = system.join(join_contract())

    assert joined.outcome == "not_supported"
    assert joined.proposal is None


def test_coordination_receipt_makes_overhead_and_refusals_visible():
    system = coordinator()
    for assignment in assignments():
        system.delegate(assignment)
    system.accept_result(results()[0])
    with pytest.raises(CoordinationRefused):
        system.accept_result(results()[0])
    system.join(join_contract())

    assert system.receipt.assignments_issued == 2
    assert system.receipt.results_accepted == 1
    assert system.receipt.results_refused == 1
    assert system.receipt.joins_attempted == 1


def test_join_creates_a_proposal_but_performs_no_outside_effect():
    system = coordinator()
    for assignment in assignments():
        system.delegate(assignment)
    for result in results():
        system.accept_result(result)

    joined = system.join(join_contract())

    assert joined.proposal is not None
    assert joined.proposal.proposed_intent.startswith("publish")
    assert not hasattr(joined.proposal, "effect_result")

