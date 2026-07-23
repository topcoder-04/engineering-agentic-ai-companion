from orders_investigation.evaluation.production import EvaluationCase
from orders_investigation.operations.learning import promote_incident, verify_regression
from chapter_late_fixtures import case, trace
from orders_investigation.runtime.journey import (
    run_orders_investigation,
    trace_orders_investigation,
)


def test_incident_becomes_owned_reproducible_regression():
    first = promote_incident("inc-17", trace(), case(), "orders-platform")
    second = promote_incident("inc-17", trace(), case(), "orders-platform")
    assert first.owner == "orders-platform" and first.failure_signature == second.failure_signature
    assert len(first.failure_signature) == 64


def test_promoted_stale_evidence_incident_rejects_original_and_accepts_correction():
    failed = run_orders_investigation(evidence_current=False)
    corrected = run_orders_investigation()
    regression = EvaluationCase(
        "orders-stale-evidence-regression",
        frozenset(failed.recorded_evidence),
        frozenset({"observe", "decide", "effect"}),
        4,
    )
    boundary = promote_incident(
        "incident-stale-evidence",
        trace_orders_investigation(failed),
        regression,
        "orders-platform",
    )

    assert verify_regression(
        boundary, trace_orders_investigation(failed)
    ).passed is False
    assert verify_regression(
        boundary, trace_orders_investigation(corrected)
    ).passed is True
