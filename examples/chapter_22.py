"""Chapter 22: trace the successful and refused Orders journeys."""

from orders_investigation.runtime.journey import (
    run_orders_investigation,
    trace_orders_investigation,
)


accepted = trace_orders_investigation(run_orders_investigation(), execution_id="accepted-22")
refused = trace_orders_investigation(
    run_orders_investigation(evidence_current=False),
    execution_id="refused-22",
)
print("CHAPTER 22 — SEMANTIC TRACE")
print("accepted", accepted.final_status, "events", [event.kind for event in accepted.events])
print("refused", refused.final_status, "last event", refused.events[-1].kind)
