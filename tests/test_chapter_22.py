from orders_investigation.evaluation.production import SemanticTrace, TraceEvent, digest


def test_trace_proves_sequence_versions_and_digests():
    events = (
        TraceEvent(1, "observe", "orders", digest("request"), digest("cpu=82")),
        TraceEvent(2, "decide", "orders", digest("cpu=82"), digest("inspect-pool")),
    )
    trace = SemanticTrace("exec-22", "agent-v2", "restricted", "policy-v3", events, "completed")
    assert trace.validate() == ()


def test_invalid_trace_is_refused_by_explicit_integrity_reasons():
    broken = SemanticTrace(
        "x", "", "m", "", (TraceEvent(2, "observe", "x", "", ""),), "completed"
    )
    assert broken.validate() == (
        "event_sequence_invalid",
        "agent_version_missing",
        "policy_version_missing",
        "event_digest_missing",
    )
