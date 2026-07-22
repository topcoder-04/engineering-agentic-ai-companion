from orders_investigation.evaluation.production import ReleaseThresholds, evaluate, gate_release
from chapter_late_fixtures import case, trace
from orders_investigation.runtime.journey import gate_orders_release, run_orders_investigation


def test_release_gate_fails_closed_without_evaluation_evidence():
    assert gate_release([], [], ReleaseThresholds(.95)).reasons == ("evaluation_evidence_missing",)


def test_release_gate_combines_quality_and_safety_vetoes():
    good = evaluate(trace(), case())
    unsafe = evaluate(trace(kinds=("observe", "forbidden_write", "effect")), case())
    decision = gate_release([good, unsafe], [trace(), trace()], ReleaseThresholds(.9))
    assert set(decision.reasons) == {"pass_rate_below_threshold", "safety_failure_budget_exceeded"}


def test_refused_orders_effect_stops_the_candidate_release():
    accepted = run_orders_investigation()
    refused = run_orders_investigation(evidence_current=False)

    assert gate_orders_release((accepted,)).allowed is True
    blocked = gate_orders_release((accepted, refused))
    assert blocked.allowed is False
    assert set(blocked.reasons) == {
        "pass_rate_below_threshold",
        "safety_failure_budget_exceeded",
    }
