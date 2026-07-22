"""Chapter 37: derive launch risk from the complete Orders proof chain."""

from orders_investigation.runtime.journey import run_orders_launch


allowed = run_orders_launch()
denied = run_orders_launch(faults=("none", "stale_evidence"))
print("CHAPTER 37 — EXECUTABLE LAUNCH RISK")
print("complete evidence", allowed.evidence, "decision", allowed.decision)
print(
    "executed path",
    [step.kind for step in allowed.execution.registered.journey.steps],
)
print("stale-evidence campaign", denied.evidence, "decision", denied.decision)
print("denied candidate executed", denied.execution is not None)
