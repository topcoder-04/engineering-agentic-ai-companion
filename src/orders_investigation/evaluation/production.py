"""Deterministic production controls used by Part 4.

These types do not evaluate prose or call a model.  They preserve the facts an
independent evaluator, release gate, and fleet controller need to make exact
claims about one recorded trajectory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Callable, Iterable, Mapping, Any


def digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TraceEvent:
    sequence: int
    kind: str
    component: str
    input_digest: str
    output_digest: str
    evidence_ids: tuple[str, ...] = ()
    decision_reason: str = ""
    duration_ms: int = 0
    input_units: int = 0
    output_units: int = 0
    data_class: str = "standard"


@dataclass(frozen=True)
class SemanticTrace:
    execution_id: str
    agent_version: str
    model_profile: str
    policy_version: str
    events: tuple[TraceEvent, ...]
    final_status: str

    def validate(self) -> tuple[str, ...]:
        reasons: list[str] = []
        if [event.sequence for event in self.events] != list(range(1, len(self.events) + 1)):
            reasons.append("event_sequence_invalid")
        if not self.agent_version:
            reasons.append("agent_version_missing")
        if not self.policy_version:
            reasons.append("policy_version_missing")
        if any(not event.input_digest or not event.output_digest for event in self.events):
            reasons.append("event_digest_missing")
        return tuple(reasons)

    @property
    def total_units(self) -> int:
        return sum(e.input_units + e.output_units for e in self.events)

    @property
    def total_duration_ms(self) -> int:
        return sum(e.duration_ms for e in self.events)


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    required_evidence: frozenset[str]
    allowed_event_kinds: frozenset[str]
    maximum_actions: int
    required_final_status: str = "completed"


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    passed: bool
    dimensions: dict[str, bool]
    reasons: tuple[str, ...]


JudgeCall = Callable[[Mapping[str, Any]], Mapping[str, Any]]


@dataclass(frozen=True)
class JudgeVerdict:
    evaluator: str
    dimension: str
    passed: bool
    confidence: str
    reason: str
    cited_sequences: tuple[int, ...]


def judge_trajectory(
    trace: SemanticTrace,
    dimension: str,
    rubric: str,
    call_model: JudgeCall,
) -> JudgeVerdict:
    """Call a model through a typed boundary; reject unsupported verdicts."""
    payload = {
        "task": "evaluate_trajectory",
        "dimension": dimension,
        "rubric": rubric,
        "trace": [
            {
                "sequence": event.sequence,
                "kind": event.kind,
                "component": event.component,
                "evidence_ids": list(event.evidence_ids),
                "decision_reason": event.decision_reason,
            }
            for event in trace.events
        ],
        "response_schema": {
            "passed": "boolean",
            "confidence": "HIGH|MEDIUM|LOW",
            "reason": "string",
            "cited_sequences": "integer[]",
        },
    }
    raw = call_model(payload)
    citations = tuple(int(item) for item in raw.get("cited_sequences", ()))
    valid_sequences = {event.sequence for event in trace.events}
    if not citations or not set(citations) <= valid_sequences:
        raise ValueError("judge_citations_invalid")
    confidence = str(raw.get("confidence", ""))
    if confidence not in {"HIGH", "MEDIUM", "LOW"}:
        raise ValueError("judge_confidence_invalid")
    return JudgeVerdict(
        evaluator=str(raw.get("evaluator", "model-judge")),
        dimension=dimension,
        passed=bool(raw["passed"]),
        confidence=confidence,
        reason=str(raw["reason"]),
        cited_sequences=citations,
    )


def evaluate(trace: SemanticTrace, case: EvaluationCase) -> EvaluationResult:
    evidence = {item for event in trace.events for item in event.evidence_ids}
    dimensions = {
        "trace_integrity": not trace.validate(),
        "evidence_sufficiency": case.required_evidence <= evidence,
        "path_compliance": all(e.kind in case.allowed_event_kinds for e in trace.events),
        "action_efficiency": len(trace.events) <= case.maximum_actions,
        "outcome": trace.final_status == case.required_final_status,
    }
    reasons = tuple(name for name, passed in dimensions.items() if not passed)
    return EvaluationResult(case.case_id, not reasons, dimensions, reasons)


@dataclass(frozen=True)
class ReleaseThresholds:
    minimum_pass_rate: float
    maximum_safety_failures: int = 0
    maximum_p95_duration_ms: int = 30_000
    maximum_average_units: float = 10_000


@dataclass(frozen=True)
class ReleaseDecision:
    allowed: bool
    reasons: tuple[str, ...]


def gate_release(
    results: Iterable[EvaluationResult],
    traces: Iterable[SemanticTrace],
    thresholds: ReleaseThresholds,
) -> ReleaseDecision:
    results, traces = tuple(results), tuple(traces)
    if not results or not traces:
        return ReleaseDecision(False, ("evaluation_evidence_missing",))
    reasons: list[str] = []
    pass_rate = sum(result.passed for result in results) / len(results)
    safety_failures = sum(not result.dimensions.get("path_compliance", False) for result in results)
    durations = sorted(trace.total_duration_ms for trace in traces)
    p95 = durations[max(0, int((len(durations) - 1) * .95))]
    average_units = sum(trace.total_units for trace in traces) / len(traces)
    if pass_rate < thresholds.minimum_pass_rate:
        reasons.append("pass_rate_below_threshold")
    if safety_failures > thresholds.maximum_safety_failures:
        reasons.append("safety_failure_budget_exceeded")
    if p95 > thresholds.maximum_p95_duration_ms:
        reasons.append("latency_budget_exceeded")
    if average_units > thresholds.maximum_average_units:
        reasons.append("unit_budget_exceeded")
    return ReleaseDecision(not reasons, tuple(reasons))


@dataclass(frozen=True)
class RedactedEvent:
    sequence: int
    kind: str
    component: str
    input_digest: str
    output_digest: str
    evidence_count: int
    duration_ms: int
    units: int


def operational_view(trace: SemanticTrace) -> tuple[RedactedEvent, ...]:
    """Expose useful operational fields without raw prompts or evidence."""
    return tuple(
        RedactedEvent(
            event.sequence, event.kind, event.component, event.input_digest,
            event.output_digest, len(event.evidence_ids), event.duration_ms,
            event.input_units + event.output_units,
        )
        for event in trace.events
    )


@dataclass(frozen=True)
class Variation:
    variation_id: str
    model_profile: str
    dependency_fault: str = "none"
    timing_offset_ms: int = 0
    evidence_order: tuple[str, ...] = ()


def variation_matrix(
    models: Iterable[str], faults: Iterable[str], timing_offsets: Iterable[int]
) -> tuple[Variation, ...]:
    rows: list[Variation] = []
    for model in models:
        for fault in faults:
            for offset in timing_offsets:
                key = f"{model}|{fault}|{offset}"
                rows.append(Variation(digest(key)[:12], model, fault, offset))
    return tuple(rows)


@dataclass(frozen=True)
class RegressionBoundary:
    incident_id: str
    case: EvaluationCase
    failure_signature: str
    owner: str


def promote_incident(
    incident_id: str,
    failed_trace: SemanticTrace,
    corrected_case: EvaluationCase,
    owner: str,
) -> RegressionBoundary:
    signature = digest("|".join(
        [failed_trace.agent_version, failed_trace.policy_version]
        + [event.kind + ":" + event.decision_reason for event in failed_trace.events]
    ))
    return RegressionBoundary(incident_id, corrected_case, signature, owner)
