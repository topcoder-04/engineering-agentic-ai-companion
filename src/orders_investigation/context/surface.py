from __future__ import annotations

import json
from dataclasses import dataclass

from orders_investigation.domain.incident import Incident
from orders_investigation.graph.tasks import InvestigationGraph


@dataclass(frozen=True)
class DecisionSurface:
    prompt: str
    included: tuple[str, ...]
    omitted: tuple[str, ...]


def build_decision_surface(
    incident: Incident,
    graph: InvestigationGraph,
    *,
    prior_model_reason: str | None = None,
    retrieved_knowledge: tuple[dict[str, str], ...] = (),
    active_direction: dict[str, object] | None = None,
    max_chars: int = 1800,
) -> DecisionSurface:
    required = {
        "service": incident.service,
        "environment": incident.environment,
        "goal": "Connect order timeouts to the responsible workload and trigger, then save the incident report.",
        "recorded_evidence": {
            key.value: evidence.value for key, evidence in incident.recorded_evidence.items()
        },
        "missing_evidence": [key.value for key in incident.missing_evidence],
        "ready_tasks": list(graph.ready_ids()),
    }
    optional = {}
    if prior_model_reason:
        optional["prior_model_reason"] = prior_model_reason
    if retrieved_knowledge:
        optional["retrieved_knowledge"] = list(retrieved_knowledge)
    if active_direction:
        optional["active_direction"] = active_direction

    payload = {**required, **optional}
    prompt = json.dumps(payload, sort_keys=True)
    omitted: tuple[str, ...] = ()
    if len(prompt) > max_chars and optional:
        prompt = json.dumps(required, sort_keys=True)
        omitted = ("prior_model_reason",)
    if len(prompt) > max_chars:
        raise ValueError("context_budget_too_small_for_required_facts")
    return DecisionSurface(prompt, tuple(required) + tuple(key for key in optional if key not in omitted), omitted)

