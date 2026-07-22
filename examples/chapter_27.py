"""Chapter 27: turn one failure into an owned regression boundary."""
from orders_investigation.evaluation.production import EvaluationCase
from orders_investigation.operations.learning import promote_incident, verify_regression
from orders_investigation.runtime.journey import (
    run_orders_investigation,
    trace_orders_investigation,
)

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
print("CHAPTER 27 — OWNED REGRESSION")
print("incident", boundary.incident_id, "owner", boundary.owner, "signature", boundary.failure_signature[:12])
print("original still fails", verify_regression(boundary, trace_orders_investigation(failed)).passed)
print("corrected path passes", verify_regression(boundary, trace_orders_investigation(corrected)).passed)
