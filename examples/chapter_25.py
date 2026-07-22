"""Chapter 25: observe the real Orders path without exposing its evidence."""

from orders_investigation.operations.observability import operational_view
from orders_investigation.runtime.journey import (
    run_orders_investigation,
    trace_orders_investigation,
)

accepted = operational_view(trace_orders_investigation(run_orders_investigation()))
refused = operational_view(
    trace_orders_investigation(run_orders_investigation(evidence_current=False))
)
print("CHAPTER 25 — REDACTED OPERATIONS VIEW")
print("accepted events", len(accepted), "last kind", accepted[-1].kind)
print("refused events", len(refused), "last kind", refused[-1].kind)
print("raw evidence exposed", hasattr(accepted[0], "raw_evidence"))
