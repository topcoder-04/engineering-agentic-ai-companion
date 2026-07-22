"""Chapter 37: executable launch-risk posture."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskTier:
    name: str
    maximum_effect: str
    human_approval: bool
    minimum_evidence_cases: int
    safety_failures_allowed: int = 0


@dataclass(frozen=True)
class LaunchEvidence:
    cases: int
    safety_failures: int
    owner_present: bool
    rollback_proven: bool
    caller_authority_proven: bool
    data_boundary_proven: bool


def approve_launch(tier: RiskTier, evidence: LaunchEvidence) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if evidence.cases < tier.minimum_evidence_cases:
        reasons.append("insufficient_evaluation_cases")
    if evidence.safety_failures > tier.safety_failures_allowed:
        reasons.append("safety_failure_budget_exceeded")
    if not evidence.owner_present:
        reasons.append("owner_missing")
    if not evidence.rollback_proven:
        reasons.append("rollback_unproven")
    if not evidence.caller_authority_proven:
        reasons.append("caller_authority_unproven")
    if not evidence.data_boundary_proven:
        reasons.append("data_boundary_unproven")
    return not reasons, tuple(reasons)
