"""Chapter 35: runtime ownership remains a launch requirement."""

from orders_investigation.runtime.journey import (
    orders_lifecycle_ownership,
    run_owned_orders_investigation,
)

accepted = run_owned_orders_investigation(orders_lifecycle_ownership())
print("CHAPTER 35 — LIFECYCLE OWNERSHIP")
print("owned candidate completed", accepted.registered.journey.completed)
try:
    run_owned_orders_investigation(orders_lifecycle_ownership(owner=""))
except ValueError as exc:
    print("missing owner refused", exc)
