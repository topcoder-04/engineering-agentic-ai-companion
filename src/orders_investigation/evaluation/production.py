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



