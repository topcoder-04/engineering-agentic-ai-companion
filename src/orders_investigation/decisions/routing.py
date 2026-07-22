from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum


class CostClass(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class LatencyClass(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class DataClass(StrEnum):
    STANDARD = "standard"
    RESTRICTED = "restricted"


@dataclass(frozen=True)
class JudgmentRequirements:
    capability: str
    max_cost_class: CostClass
    max_latency_class: LatencyClass
    data_class: DataClass


@dataclass(frozen=True)
class ModelProfile:
    source_id: str
    model_id: str
    capabilities: frozenset[str]
    cost_class: CostClass
    latency_class: LatencyClass
    accepts_restricted_data: bool


@dataclass(frozen=True)
class CandidateEvaluation:
    source_id: str
    accepted: bool
    reason: str


@dataclass(frozen=True)
class RoutingDecision:
    selected: ModelProfile | None
    evaluations: tuple[CandidateEvaluation, ...]
    used_fallback: bool


def _evaluate(
    profile: ModelProfile,
    requirements: JudgmentRequirements,
    *,
    unavailable: frozenset[str],
) -> CandidateEvaluation:
    if profile.source_id in unavailable:
        return CandidateEvaluation(profile.source_id, False, "source_unavailable")
    if requirements.capability not in profile.capabilities:
        return CandidateEvaluation(profile.source_id, False, "capability_missing")
    if profile.cost_class > requirements.max_cost_class:
        return CandidateEvaluation(profile.source_id, False, "cost_ceiling_exceeded")
    if profile.latency_class > requirements.max_latency_class:
        return CandidateEvaluation(profile.source_id, False, "latency_ceiling_exceeded")
    if (
        requirements.data_class == DataClass.RESTRICTED
        and not profile.accepts_restricted_data
    ):
        return CandidateEvaluation(profile.source_id, False, "data_rule_not_met")
    return CandidateEvaluation(profile.source_id, True, "requirements_met")


def choose_judgment_source(
    requirements: JudgmentRequirements,
    profiles: tuple[ModelProfile, ...],
    *,
    unavailable: frozenset[str] = frozenset(),
) -> RoutingDecision:
    if not profiles:
        raise ValueError("model_profiles_required")

    evaluations: list[CandidateEvaluation] = []
    selected: ModelProfile | None = None
    selected_index: int | None = None
    for index, profile in enumerate(profiles):
        result = _evaluate(profile, requirements, unavailable=unavailable)
        evaluations.append(result)
        if result.accepted:
            selected = profile
            selected_index = index
            break

    return RoutingDecision(
        selected=selected,
        evaluations=tuple(evaluations),
        used_fallback=selected_index is not None and selected_index > 0,
    )


def orders_model_profiles() -> tuple[ModelProfile, ...]:
    """Configured demonstration policy, not measured model performance."""
    return (
        ModelProfile(
            source_id="quick-choice",
            model_id="configured-quick-model",
            capabilities=frozenset({"task_choice"}),
            cost_class=CostClass.LOW,
            latency_class=LatencyClass.LOW,
            accepts_restricted_data=False,
        ),
        ModelProfile(
            source_id="deeper-choice",
            model_id="configured-reasoning-model",
            capabilities=frozenset({"task_choice", "generated_analysis"}),
            cost_class=CostClass.MEDIUM,
            latency_class=LatencyClass.MEDIUM,
            accepts_restricted_data=False,
        ),
        ModelProfile(
            source_id="private-analysis",
            model_id="configured-private-model",
            capabilities=frozenset({"task_choice", "generated_analysis"}),
            cost_class=CostClass.HIGH,
            latency_class=LatencyClass.HIGH,
            accepts_restricted_data=True,
        ),
    )

