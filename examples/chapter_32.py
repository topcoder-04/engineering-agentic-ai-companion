"""Chapter 32: placement must satisfy every data boundary."""
from orders_investigation.runtime.journey import (
    orders_data_boundary,
    orders_execution_targets,
    run_placed_orders_investigation,
)

accepted = run_placed_orders_investigation(
    orders_data_boundary(), orders_execution_targets()
)
print("CHAPTER 32 — DATA PLACEMENT")
print("selected target", accepted.target_id, "completed", accepted.registered.journey.completed)
try:
    run_placed_orders_investigation(
        orders_data_boundary(region="eu-west-1"), orders_execution_targets()
    )
except ValueError as exc:
    print("wrong residency refused", exc)
