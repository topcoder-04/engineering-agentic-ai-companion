"""Chapter 31: caller identity and delegated authority."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CallerIdentity:
    subject: str
    tenant_id: str
    roles: frozenset[str]


@dataclass(frozen=True)
class Delegation:
    delegation_id: str
    subject: str
    tenant_id: str
    agent_id: str
    allowed_actions: frozenset[str]
    expires_at: datetime


def authorize(identity: CallerIdentity, delegation: Delegation, agent_id: str, action: str,
              now: datetime | None = None) -> tuple[bool, tuple[str, ...]]:
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []
    if delegation.subject != identity.subject:
        reasons.append("delegated_subject_mismatch")
    if delegation.tenant_id != identity.tenant_id:
        reasons.append("delegated_tenant_mismatch")
    if delegation.agent_id != agent_id:
        reasons.append("delegated_agent_mismatch")
    if action not in delegation.allowed_actions:
        reasons.append("action_not_delegated")
    if now >= delegation.expires_at:
        reasons.append("delegation_expired")
    return not reasons, tuple(reasons)
