"""Chapter 22: record a trajectory that can be checked later."""
from orders_investigation.evaluation.production import SemanticTrace, TraceEvent, digest

events = (TraceEvent(1, "observe", "orders", digest("request"), digest("cpu=82"), ("cpu",), duration_ms=18),
          TraceEvent(2, "decide", "orders", digest("cpu=82"), digest("inspect-pool"), decision_reason="missing connections", duration_ms=7))
trace = SemanticTrace("exec-22", "agent-v2", "restricted", "policy-v3", events, "in_progress")
print("CHAPTER 22 — SEMANTIC TRACE")
print("integrity", trace.validate(), "events", len(trace.events), "duration_ms", trace.total_duration_ms)

