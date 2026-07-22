"""Chapter 34: artifact-bound conformance and release evidence."""

from dataclasses import dataclass
from typing import Iterable

from ..identity import AgentContract


@dataclass(frozen=True)
class ConformanceReceipt:
    candidate_digest: str
    contract_digest: str
    suite_version: str
    passed_checks: frozenset[str]
    failed_checks: frozenset[str]


def release_conforms(candidate_digest: str, contract: AgentContract,
                     receipt: ConformanceReceipt, required_checks: Iterable[str]) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if receipt.candidate_digest != candidate_digest:
        reasons.append("candidate_evidence_mismatch")
    if receipt.contract_digest != contract.manifest_digest:
        reasons.append("contract_evidence_mismatch")
    reasons.extend(
        f"required_check_missing:{item}"
        for item in sorted(set(required_checks) - receipt.passed_checks)
    )
    if receipt.failed_checks:
        reasons.append("conformance_check_failed")
    return not reasons, tuple(reasons)
