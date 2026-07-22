"""Chapter 25 safe operational views."""

from dataclasses import dataclass

from orders_investigation.evaluation.production import SemanticTrace


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
    """Expose operational fields without raw prompts or evidence values."""
    return tuple(
        RedactedEvent(
            event.sequence,
            event.kind,
            event.component,
            event.input_digest,
            event.output_digest,
            len(event.evidence_ids),
            event.duration_ms,
            event.input_units + event.output_units,
        )
        for event in trace.events
    )

__all__ = ["RedactedEvent", "operational_view"]
