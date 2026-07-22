"""Chapter 27 bounded incident-to-regression promotion."""

from dataclasses import dataclass

from orders_investigation.evaluation.production import (
    EvaluationCase,
    EvaluationResult,
    SemanticTrace,
    digest,
    evaluate,
)


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


def verify_regression(
    boundary: RegressionBoundary,
    candidate_trace: SemanticTrace,
) -> EvaluationResult:
    """Run the promoted case against a candidate trajectory."""
    return evaluate(candidate_trace, boundary.case)

__all__ = ["RegressionBoundary", "promote_incident", "verify_regression"]
