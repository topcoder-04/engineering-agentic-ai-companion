"""Chapter 23: evaluate the path produced by the Orders investigation."""

from orders_investigation.runtime.journey import (
    evaluate_orders_investigation,
    run_orders_investigation,
)


accepted = evaluate_orders_investigation(run_orders_investigation())
refused = evaluate_orders_investigation(run_orders_investigation(evidence_current=False))
print("CHAPTER 23 — PATH EVALUATION")
print("accepted", accepted.passed, "dimensions", accepted.dimensions)
print("refused", refused.passed, "reasons", refused.reasons)
