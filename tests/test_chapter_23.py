import pytest
from orders_investigation.evaluation.production import judge_trajectory
from chapter_late_fixtures import trace
from orders_investigation.runtime.journey import (
    evaluate_orders_investigation,
    run_orders_investigation,
)


def test_judge_must_cite_recorded_trace_events():
    verdict = judge_trajectory(trace(), "causality", "cite support", lambda _: {
        "passed": True, "confidence": "HIGH", "reason": "supported", "cited_sequences": [1]})
    assert verdict.cited_sequences == (1,)


def test_judge_rejects_uncited_opinion():
    with pytest.raises(ValueError, match="judge_citations_invalid"):
        judge_trajectory(trace(), "causality", "cite support", lambda _: {
            "passed": True, "confidence": "HIGH", "reason": "guess", "cited_sequences": []})


def test_refused_orders_effect_cannot_pass_trajectory_evaluation():
    accepted = evaluate_orders_investigation(run_orders_investigation())
    refused = evaluate_orders_investigation(
        run_orders_investigation(evidence_current=False)
    )

    assert accepted.passed is True
    assert refused.passed is False
    assert set(refused.reasons) == {"path_compliance", "outcome"}
