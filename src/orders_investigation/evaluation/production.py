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
