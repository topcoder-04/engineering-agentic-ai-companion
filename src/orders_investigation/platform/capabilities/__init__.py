"""Chapter 30: capability declarations and admission."""

from dataclasses import dataclass

from ..identity import AgentContract


@dataclass(frozen=True)
class CapabilityProfile:
    capability_id: str
    model_profiles: frozenset[str]
    tool_contracts: frozenset[str]
    policy_bundles: frozenset[str]
    data_classes: frozenset[str]


def admit_contract(contract: AgentContract, profile: CapabilityProfile) -> tuple[str, ...]:
    reasons: list[str] = []
    if contract.model_profile not in profile.model_profiles:
        reasons.append("model_profile_not_approved")
    if not set(contract.tool_contracts) <= profile.tool_contracts:
        reasons.append("tool_contract_not_approved")
    if contract.policy_bundle not in profile.policy_bundles:
        reasons.append("policy_bundle_not_approved")
    if not contract.data_classes <= profile.data_classes:
        reasons.append("data_class_not_approved")
    return tuple(reasons)
