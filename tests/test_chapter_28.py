import pytest
from orders_investigation.evaluation.production import ReleaseDecision
from orders_investigation.operations.fleet import (
    Cell,
    FleetRequest,
    Rollout,
    route,
    route_released_candidate,
)
from orders_investigation.runtime.journey import gate_orders_release, run_orders_investigation


def test_fleet_routes_only_to_exact_healthy_capacity_match():
    cells = (Cell("full", "us", "v2", "p3", 1, 1, True, "canary"),
             Cell("ready", "us", "v2", "p3", 2, 0, True, "canary"))
    assert route(cells, FleetRequest("r", "us", "v2", "p3", "canary")).cell_id == "ready"


def test_failed_gate_stops_rollout_and_prevents_advance():
    rollout = Rollout("canary")
    rollout.observe(ReleaseDecision(False, ("safety_failure_budget_exceeded",)))
    with pytest.raises(ValueError, match="stopped_rollout_cannot_advance"):
        rollout.advance()


def test_candidate_cannot_enter_fleet_when_orders_regression_fails_release_gate():
    cells = (Cell("ready", "us", "orders-agent-v1", "orders-report-v1", 2, 0, True, "canary"),)
    request = FleetRequest("r", "us", "orders-agent-v1", "orders-report-v1", "canary")
    accepted = run_orders_investigation()
    refused = run_orders_investigation(evidence_current=False)

    admitted = route_released_candidate(cells, request, gate_orders_release((accepted,)))
    blocked = route_released_candidate(
        cells, request, gate_orders_release((accepted, refused))
    )
    assert admitted.cell_id == "ready"
    assert blocked.cell_id is None
    assert blocked.reasons == (
        "release_denied:pass_rate_below_threshold",
        "release_denied:safety_failure_budget_exceeded",
    )
