from orders_investigation.runtime.boundary import ORDERS_BOUNDARY, Request
from orders_investigation.environment.requests import OPENING_OBSERVATION_REQUESTS


def test_four_opening_observation_requests_are_declared_and_permitted() -> None:
    assert set(OPENING_OBSERVATION_REQUESTS) == {
        "inspect_connection_pool",
        "inspect_database_error_rate",
        "inspect_database_topology",
        "inspect_dependency_health",
    }
    assert all(ORDERS_BOUNDARY.allows(request) for request in OPENING_OBSERVATION_REQUESTS.values())


def test_incident_report_update_is_allowed_without_an_opaque_report_id() -> None:
    request = Request(
        "update_report", "incident_record", "orders-production", "incident_report", "save"
    )
    assert ORDERS_BOUNDARY.allows(request)


def test_other_environment_and_rollback_are_rejected_before_outside_work() -> None:
    other_environment = Request(
        "observe", "service_metrics", "payments-production", "payments-api", "latency"
    )
    rollback = Request(
        "rollback", "deployment_pipeline", "orders-production", "orders-release", "latest"
    )
    assert not ORDERS_BOUNDARY.allows(other_environment)
    assert not ORDERS_BOUNDARY.allows(rollback)


def test_unknown_operations_fail_closed() -> None:
    restart = Request(
        "restart", "service_metrics", "orders-production", "orders-api", "latest"
    )
    assert not ORDERS_BOUNDARY.allows(restart)

