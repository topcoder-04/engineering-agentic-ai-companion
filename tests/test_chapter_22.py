from orders_investigation.evaluation.production import SemanticTrace, TraceEvent, digest
from orders_investigation.runtime.journey import (
    run_orders_investigation,
    trace_orders_investigation,
)


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


def test_semantic_trace_is_emitted_by_the_real_orders_effect_path():
    accepted = trace_orders_investigation(run_orders_investigation())
    refused = trace_orders_investigation(run_orders_investigation(evidence_current=False))

    assert accepted.validate() == ()
    assert accepted.final_status == "completed"
    assert tuple(event.kind for event in accepted.events) == (
        "observe", "decide", "observe", "effect"
    )
    assert refused.final_status == "refused"
    assert refused.events[-1].kind == "effect_refused"
    assert refused.events[-1].output_digest != accepted.events[-1].output_digest
