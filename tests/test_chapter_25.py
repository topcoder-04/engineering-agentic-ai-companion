from orders_investigation.operations.observability import operational_view
from chapter_late_fixtures import trace


def test_operational_view_is_useful_without_raw_content():
    event = operational_view(trace())[0]
    assert event.evidence_count == 2 and event.units == 20
    assert not hasattr(event, "prompt") and not hasattr(event, "raw_evidence")
