from orders_investigation.platform.risk import LaunchEvidence, RiskTier, approve_launch


def test_launch_risk_preserves_independent_vetoes():
    tier = RiskTier("consequential", "bounded-write", True, 100)
    denied = approve_launch(tier, LaunchEvidence(90, 1, False, False, False, False))
    assert denied == (False, ("insufficient_evaluation_cases", "safety_failure_budget_exceeded", "owner_missing",
                              "rollback_unproven", "caller_authority_unproven", "data_boundary_unproven"))


def test_complete_launch_evidence_is_admitted():
    tier = RiskTier("consequential", "bounded-write", True, 100)
    assert approve_launch(tier, LaunchEvidence(140, 0, True, True, True, True)) == (True, ())
