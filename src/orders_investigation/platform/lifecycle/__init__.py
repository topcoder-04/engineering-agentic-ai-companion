"""Chapter 35: owned, expiring operational exceptions."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ExceptionGrant:
    exception_id: str
    owner: str
    scope: str
    expires_at: datetime
    compensating_controls: tuple[str, ...]
    waivable: bool = True


@dataclass(frozen=True)
class LifecycleOwnership:
    agent_id: str
    version: str
    owner: str
    runbook: str
    rollback_owner: str


def validate_ownership(record: LifecycleOwnership) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not record.owner:
        reasons.append("lifecycle_owner_missing")
    if not record.runbook:
        reasons.append("runbook_missing")
    if not record.rollback_owner:
        reasons.append("rollback_owner_missing")
    return not reasons, tuple(reasons)


def validate_exception(grant: ExceptionGrant, requested_scope: str,
                       now: datetime | None = None) -> tuple[bool, tuple[str, ...]]:
    now = now or datetime.now(timezone.utc)
    reasons: list[str] = []
    if not grant.waivable:
        reasons.append("boundary_not_waivable")
    if grant.scope != requested_scope:
        reasons.append("exception_scope_mismatch")
    if now >= grant.expires_at:
        reasons.append("exception_expired")
    if not grant.owner:
        reasons.append("exception_owner_missing")
    if not grant.compensating_controls:
        reasons.append("compensating_control_missing")
    return not reasons, tuple(reasons)
