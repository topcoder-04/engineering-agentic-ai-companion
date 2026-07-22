"""Chapter 25: operational visibility without raw evidence."""
from orders_investigation.evaluation.production import SemanticTrace, TraceEvent
from orders_investigation.operations.observability import operational_view

trace = SemanticTrace("exec-25", "v2", "restricted", "p3", (TraceEvent(1, "observe", "orders", "request-digest", "result-digest", ("cpu", "connections"), duration_ms=15, input_units=8, output_units=4),), "completed")
event = operational_view(trace)[0]
print("CHAPTER 25 — REDACTED OPERATIONS VIEW")
print("component", event.component, "evidence_count", event.evidence_count, "units", event.units, "raw_evidence_exposed", hasattr(event, "raw_evidence"))
