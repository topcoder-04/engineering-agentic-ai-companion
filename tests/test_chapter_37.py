from orders_investigation.platform.risk import LaunchEvidence, RiskTier, approve_launch
from orders_investigation.runtime.journey import (
    orders_lifecycle_ownership,
    run_orders_launch,
)


def test_launch_risk_preserves_independent_vetoes():
    tier = RiskTier("consequential", "bounded-write", True, 100)
    denied = approve_launch(tier, LaunchEvidence(90, 1, False, False, False, False))
    assert denied == (False, ("insufficient_evaluation_cases", "safety_failure_budget_exceeded", "owner_missing",
                              "rollback_unproven", "caller_authority_unproven", "data_boundary_unproven"))


def test_complete_launch_evidence_is_admitted():
    tier = RiskTier("consequential", "bounded-write", True, 100)
    assert approve_launch(tier, LaunchEvidence(140, 0, True, True, True, True)) == (True, ())


def test_complete_orders_proof_chain_launches_and_executes_one_spine():
    launched = run_orders_launch()

    assert launched.evidence == LaunchEvidence(4, 0, True, True, True, True)
    assert launched.decision == (True, ())
    assert launched.execution is not None
    assert launched.execution.registered.journey.completed is True
    assert tuple(step.kind for step in launched.execution.registered.journey.steps) == (
        "observe", "decide", "observe", "effect"
    )


def test_failed_variations_and_missing_owner_are_independent_launch_vetoes():
    unsafe = run_orders_launch(faults=("none", "stale_evidence"))
    unowned = run_orders_launch(ownership=orders_lifecycle_ownership(owner=""))

    assert unsafe.evidence.cases == 8
    assert unsafe.evidence.safety_failures == 4
    assert unsafe.decision == (False, ("safety_failure_budget_exceeded",))
    assert unsafe.execution is None
    assert unowned.decision == (False, ("owner_missing",))
    assert unowned.execution is None
