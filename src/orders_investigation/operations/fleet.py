"""Chapter 28 fleet routing and rollout limits."""

from dataclasses import dataclass, field
from typing import Iterable

from orders_investigation.evaluation.production import ReleaseDecision


@dataclass(frozen=True)
class Cell:
    cell_id: str
    region: str
    agent_version: str
    policy_version: str
    capacity: int
    inflight: int
    healthy: bool
    rollout_stage: str


@dataclass(frozen=True)
class FleetRequest:
    request_id: str
    region: str
    agent_version: str
    policy_version: str
    rollout_stage: str


@dataclass(frozen=True)
class RouteDecision:
    cell_id: str | None
    reasons: tuple[str, ...]


def route(cells: Iterable[Cell], request: FleetRequest) -> RouteDecision:
    refusals: list[str] = []
    for cell in sorted(cells, key=lambda item: item.cell_id):
        mismatches = []
        if cell.region != request.region:
            mismatches.append("location_mismatch")
        if cell.agent_version != request.agent_version:
            mismatches.append("agent_version_mismatch")
        if cell.policy_version != request.policy_version:
            mismatches.append("policy_version_mismatch")
        if cell.rollout_stage != request.rollout_stage:
            mismatches.append("rollout_stage_mismatch")
        if not cell.healthy:
            mismatches.append("cell_unhealthy")
        if cell.inflight >= cell.capacity:
            mismatches.append("cell_at_capacity")
        if not mismatches:
            return RouteDecision(cell.cell_id, ())
        refusals.extend(f"{cell.cell_id}:{reason}" for reason in mismatches)
    return RouteDecision(None, tuple(refusals) or ("no_cells_configured",))


def route_released_candidate(
    cells: Iterable[Cell],
    request: FleetRequest,
    release: ReleaseDecision,
) -> RouteDecision:
    """Refuse fleet admission before routing when evaluation stopped the release."""
    if not release.allowed:
        return RouteDecision(
            None,
            tuple(f"release_denied:{reason}" for reason in release.reasons),
        )
    return route(cells, request)


@dataclass
class Rollout:
    stage: str
    stopped: bool = False
    reasons: list[str] = field(default_factory=list)

    def observe(self, decision: ReleaseDecision) -> None:
        if not decision.allowed:
            self.stopped = True
            self.reasons.extend(decision.reasons)

    def advance(self) -> None:
        if self.stopped:
            raise ValueError("stopped_rollout_cannot_advance")

__all__ = [
    "Cell",
    "FleetRequest",
    "Rollout",
    "RouteDecision",
    "route",
    "route_released_candidate",
]
