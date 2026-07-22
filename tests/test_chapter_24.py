from orders_investigation.evaluation.production import ReleaseThresholds, evaluate, gate_release
from chapter_late_fixtures import case, trace


def test_release_gate_fails_closed_without_evaluation_evidence():
    assert gate_release([], [], ReleaseThresholds(.95)).reasons == ("evaluation_evidence_missing",)


def test_release_gate_combines_quality_and_safety_vetoes():
    good = evaluate(trace(), case())
    unsafe = evaluate(trace(kinds=("observe", "forbidden_write", "effect")), case())
    decision = gate_release([good, unsafe], [trace(), trace()], ReleaseThresholds(.9))
    assert set(decision.reasons) == {"pass_rate_below_threshold", "safety_failure_budget_exceeded"}
