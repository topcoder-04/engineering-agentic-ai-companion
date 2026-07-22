import pytest
from orders_investigation.evaluation.production import ReleaseDecision
from orders_investigation.operations.fleet import Cell, FleetRequest, Rollout, route


def test_fleet_routes_only_to_exact_healthy_capacity_match():
    cells = (Cell("full", "us", "v2", "p3", 1, 1, True, "canary"),
             Cell("ready", "us", "v2", "p3", 2, 0, True, "canary"))
    assert route(cells, FleetRequest("r", "us", "v2", "p3", "canary")).cell_id == "ready"


def test_failed_gate_stops_rollout_and_prevents_advance():
    rollout = Rollout("canary")
    rollout.observe(ReleaseDecision(False, ("safety_failure_budget_exceeded",)))
    with pytest.raises(ValueError, match="stopped_rollout_cannot_advance"):
        rollout.advance()
