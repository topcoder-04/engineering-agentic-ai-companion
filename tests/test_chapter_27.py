from orders_investigation.operations.learning import promote_incident
from chapter_late_fixtures import case, trace


def test_incident_becomes_owned_reproducible_regression():
    first = promote_incident("inc-17", trace(), case(), "orders-platform")
    second = promote_incident("inc-17", trace(), case(), "orders-platform")
    assert first.owner == "orders-platform" and first.failure_signature == second.failure_signature
    assert len(first.failure_signature) == 64
