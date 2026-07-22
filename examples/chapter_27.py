"""Chapter 27: turn one failure into an owned regression boundary."""
from orders_investigation.evaluation.production import EvaluationCase, SemanticTrace
from orders_investigation.operations.learning import promote_incident

case = EvaluationCase("orders-recovery", frozenset(), frozenset(), 0)
trace = SemanticTrace("exec-27", "v2", "restricted", "p3", (), "failed")
boundary = promote_incident("inc-27", trace, case, "orders-platform")
print("CHAPTER 27 — OWNED REGRESSION")
print("incident", boundary.incident_id, "owner", boundary.owner, "signature", boundary.failure_signature[:12])
