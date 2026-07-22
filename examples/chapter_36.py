"""Chapter 36: readers advance before writers."""
from orders_investigation.runtime.journey import (
    orders_compatibility_window,
    run_compatible_orders_investigation,
)

accepted = run_compatible_orders_investigation(
    orders_compatibility_window(), frozenset({"trace/v2"})
)
print("CHAPTER 36 — COMPATIBLE EVOLUTION")
print("compatible readers completed", accepted.registered.journey.completed)
try:
    run_compatible_orders_investigation(
        orders_compatibility_window(), frozenset({"trace/v0"})
    )
except ValueError as exc:
    print("incompatible reader refused", exc)
