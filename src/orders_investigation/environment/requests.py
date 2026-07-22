from __future__ import annotations

from orders_investigation.runtime.boundary import Request


OPENING_OBSERVATION_REQUESTS = {
    "inspect_connection_pool": Request(
        "observe", "database_monitoring", "orders-production", "orders-db", "connection_pool"
    ),
    "inspect_database_error_rate": Request(
        "observe", "database_monitoring", "orders-production", "orders-db", "error_rate"
    ),
    "inspect_database_topology": Request(
        "observe", "database_monitoring", "orders-production", "orders-db", "topology"
    ),
    "inspect_dependency_health": Request(
        "observe", "service_metrics", "orders-production", "orders-api", "dependency_health"
    ),
}

