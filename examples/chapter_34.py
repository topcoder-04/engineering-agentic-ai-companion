"""Chapter 34: bind release evidence to the exact artifact."""
from orders_investigation.runtime.journey import (
    orders_conformance_receipt,
    run_conformant_orders_investigation,
)

receipt = orders_conformance_receipt()
accepted = run_conformant_orders_investigation("candidate-orders-v1", receipt)
print("CHAPTER 34 — CONFORMANCE RECEIPT")
print("matching candidate completed", accepted.registered.journey.completed)
try:
    run_conformant_orders_investigation("candidate-orders-v2", receipt)
except ValueError as exc:
    print("different candidate refused", exc)
