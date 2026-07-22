"""Chapter 32: tenant, residency, data-class, and retention placement."""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DataBoundary:
    tenant_id: str
    data_class: str
    region: str
    retention_days: int


@dataclass(frozen=True)
class ExecutionTarget:
    target_id: str
    tenant_id: str
    accepted_data_classes: frozenset[str]
    region: str
    maximum_retention_days: int


def place(boundary: DataBoundary, targets: Iterable[ExecutionTarget]) -> str:
    refusals: list[str] = []
    for target in sorted(targets, key=lambda item: item.target_id):
        reasons = []
        if target.tenant_id != boundary.tenant_id:
            reasons.append("tenant_mismatch")
        if boundary.data_class not in target.accepted_data_classes:
            reasons.append("data_class_mismatch")
        if target.region != boundary.region:
            reasons.append("residency_mismatch")
        if target.maximum_retention_days > boundary.retention_days:
            reasons.append("retention_too_long")
        if not reasons:
            return target.target_id
        refusals.extend(f"{target.target_id}:{reason}" for reason in reasons)
    raise ValueError(",".join(refusals) or "target_missing")
