"""Chapter 31: preserve caller-bound delegated authority."""
from orders_investigation.runtime.journey import (
    orders_caller,
    orders_delegation,
    run_delegated_orders_investigation,
)

accepted = run_delegated_orders_investigation(orders_caller(), orders_delegation())
print("CHAPTER 31 — DELEGATED AUTHORITY")
print("accepted", accepted.journey.completed)
try:
    run_delegated_orders_investigation(
        orders_caller(), orders_delegation(), action="refund.issue"
    )
except ValueError as exc:
    print("wrong action refused", exc)
