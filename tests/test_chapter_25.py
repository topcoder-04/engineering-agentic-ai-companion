from orders_investigation.operations.observability import operational_view
from chapter_late_fixtures import trace
from orders_investigation.runtime.journey import (
    run_orders_investigation,
    trace_orders_investigation,
)


def test_operational_view_is_useful_without_raw_content():
    event = operational_view(trace())[0]
    assert event.evidence_count == 2 and event.units == 20
    assert not hasattr(event, "prompt") and not hasattr(event, "raw_evidence")


def test_real_orders_refusal_is_visible_without_leaking_evidence_values():
    journey = run_orders_investigation(evidence_current=False)
    view = operational_view(trace_orders_investigation(journey))

    assert view[-1].kind == "effect_refused"
    assert view[-1].evidence_count == len(journey.recorded_evidence)
    rendered = repr(view)
    assert "deploy-882 launched" not in rendered
    assert "Order completion recovered" not in rendered
