from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


class AuthorityRefused(ValueError):
    pass


@dataclass(frozen=True)
class SessionClaims:
    issuer: str
    subject: str
    audience: str
    session_id: str
    expires_at: datetime


@dataclass(frozen=True)
class VerificationEvidence:
    signature_verified: bool
    issuer_metadata_verified: bool


@dataclass(frozen=True)
class VerifiedSession:
    issuer: str
    subject: str
    audience: str
    session_id: str
    expires_at: datetime


@dataclass(frozen=True)
class DelegatedGrant:
    grant_id: str
    subject: str
    session_id: str
    audience: str
    operation: str
    resource: str
    intent_digest: str
    not_before: datetime
    expires_at: datetime


@dataclass(frozen=True)
class AuthorizedEffect:
    approval_id: str
    approval_status: str
    operation: str
    resource: str
    intent_digest: str


@dataclass(frozen=True)
class AuthorityReceipt:
    subject: str
    session_id: str
    grant_id: str
    operation: str
    resource: str
    intent_digest: str


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise AuthorityRefused("authority_time_requires_timezone")
    return value.astimezone(timezone.utc)


def verify_session(
    claims: SessionClaims,
    evidence: VerificationEvidence,
    *,
    expected_issuer: str,
    expected_audience: str,
    now: datetime,
) -> VerifiedSession:
    if not evidence.signature_verified or not evidence.issuer_metadata_verified:
        raise AuthorityRefused("session_not_cryptographically_verified")
    if claims.issuer != expected_issuer:
        raise AuthorityRefused("session_issuer_mismatch")
    if claims.audience != expected_audience:
        raise AuthorityRefused("session_audience_mismatch")
    if _utc(now) >= _utc(claims.expires_at):
        raise AuthorityRefused("session_expired")
    if not claims.subject or not claims.session_id:
        raise AuthorityRefused("session_identity_incomplete")
    return VerifiedSession(
        claims.issuer,
        claims.subject,
        claims.audience,
        claims.session_id,
        _utc(claims.expires_at),
    )


def authorize_effect(
    session: VerifiedSession,
    grant: DelegatedGrant,
    effect: AuthorizedEffect,
    *,
    expected_audience: str,
    now: datetime,
) -> AuthorityReceipt:
    current = _utc(now)
    if current >= _utc(session.expires_at):
        raise AuthorityRefused("session_expired")
    if effect.approval_status != "approved":
        raise AuthorityRefused("approval_not_approved")
    if grant.subject != session.subject:
        raise AuthorityRefused("grant_subject_mismatch")
    if grant.session_id != session.session_id:
        raise AuthorityRefused("grant_session_mismatch")
    if grant.audience != expected_audience or session.audience != expected_audience:
        raise AuthorityRefused("grant_audience_mismatch")
    if current < _utc(grant.not_before) or current >= _utc(grant.expires_at):
        raise AuthorityRefused("grant_not_current")
    if grant.operation != effect.operation:
        raise AuthorityRefused("grant_operation_mismatch")
    if grant.resource != effect.resource:
        raise AuthorityRefused("grant_resource_mismatch")
    if grant.intent_digest != effect.intent_digest:
        raise AuthorityRefused("grant_intent_mismatch")
    return AuthorityReceipt(
        subject=session.subject,
        session_id=session.session_id,
        grant_id=grant.grant_id,
        operation=effect.operation,
        resource=effect.resource,
        intent_digest=effect.intent_digest,
    )
