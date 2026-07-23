"""Chapter 27: turn one failure into an owned regression boundary."""
from orders_investigation.evaluation.production import EvaluationCase
from orders_investigation.operations.learning import promote_incident, verify_regression
from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.journey import (
    run_orders_investigation,
    trace_orders_investigation,
)

def main() -> None:
    demo = chapter_presentation(27, description=__doc__)
    failed = run_orders_investigation(evidence_current=False)
    corrected = run_orders_investigation()
    case = EvaluationCase(
        "orders-stale-evidence-regression",
        frozenset(failed.recorded_evidence),
        frozenset({"observe", "decide", "effect"}),
        4,
    )
    boundary = promote_incident(
        "inc-27", trace_orders_investigation(failed), case, "orders-platform"
    )
    original = verify_regression(boundary, trace_orders_investigation(failed))
    repaired = verify_regression(boundary, trace_orders_investigation(corrected))
    demo.scenario(1, "The incident becomes an owned executable boundary")
    demo.fields(
        (
            ("Incident", boundary.incident_id),
            ("Owner", boundary.owner),
            ("Failure signature", boundary.failure_signature[:12] + "…"),
        ),
        style="evidence",
    )
    demo.result_row(
        "Original path",
        accepted=original.passed,
        outcome="REGRESSION PASSED" if original.passed else "REGRESSION FAILED",
    )
    demo.result_row(
        "Corrected path",
        accepted=repaired.passed,
        outcome="REGRESSION PASSED" if repaired.passed else "REGRESSION FAILED",
    )
    demo.notice(
        "The lesson is now an owned case with a reproducible signature. The "
        "original path must keep failing while the corrected path passes."
    )


if __name__ == "__main__":
    main()
