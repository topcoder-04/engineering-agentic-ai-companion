"""Chapter 28: route only to an exact healthy fleet cell."""
from orders_investigation.operations.fleet import (
    Cell,
    FleetRequest,
    route_released_candidate,
)
from orders_investigation.runtime.journey import gate_orders_release, run_orders_investigation

cells = (
    Cell("full", "us", "orders-agent-v1", "orders-report-v1", 1, 1, True, "canary"),
    Cell("ready", "us", "orders-agent-v1", "orders-report-v1", 4, 1, True, "canary"),
)
request = FleetRequest("r-28", "us", "orders-agent-v1", "orders-report-v1", "canary")
accepted = run_orders_investigation()
refused = run_orders_investigation(evidence_current=False)
print("CHAPTER 28 — FLEET ROUTING")
print("accepted release", route_released_candidate(cells, request, gate_orders_release((accepted,))))
print("failed release", route_released_candidate(cells, request, gate_orders_release((accepted, refused))))
