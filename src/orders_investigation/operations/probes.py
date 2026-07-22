"""Chapter 26 deliberate variation probes."""

from dataclasses import dataclass
from typing import Iterable

from orders_investigation.evaluation.production import digest


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
    return tuple(
        Variation(digest(f"{model}|{fault}|{offset}")[:12], model, fault, offset)
        for model in models
        for fault in faults
        for offset in timing_offsets
    )

__all__ = ["Variation", "variation_matrix"]
