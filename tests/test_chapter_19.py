from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from orders_investigation.governance.approval import ApprovalIntent
from orders_investigation.governance.authority import (
    AuthorizedEffect,
    AuthorityRefused,
    DelegatedGrant,
    SessionClaims,
    VerificationEvidence,
    authorize_effect,
    verify_session,
)


NOW = datetime(2026, 7, 21, 16, 5, tzinfo=timezone.utc)
ISSUER = "https://login.example.invalid"
AUDIENCE = "orders-investigation"


def intent_digest():
    return ApprovalIntent(
        operation="publish_recovery_update",
        target="orders-incident-report",
        content="Order completion recovered; mark customer impact resolved.",
        supporting_evidence=("writer-recovery-17", "orders-recovery-17"),
    ).digest


def claims():
    return SessionClaims(
        issuer=ISSUER,
        subject="person-204",
        audience=AUDIENCE,
        session_id="session-551",
        expires_at=NOW + timedelta(minutes=20),
    )


def verification():
    return VerificationEvidence(
        signature_verified=True,
        issuer_metadata_verified=True,
    )


def session():
    return verify_session(
        claims(),
        verification(),
        expected_issuer=ISSUER,
        expected_audience=AUDIENCE,
        now=NOW,
    )


def grant():
    return DelegatedGrant(
        grant_id="grant-orders-recovery-publish",
        subject="person-204",
        session_id="session-551",
        audience=AUDIENCE,
        operation="publish_recovery_update",
        resource="orders-incident-report",
        intent_digest=intent_digest(),
        not_before=NOW - timedelta(minutes=1),
        expires_at=NOW + timedelta(minutes=10),
    )


def effect():
    return AuthorizedEffect(
        approval_id="approval-run-1077-recovery-1",
        approval_status="approved",
        operation="publish_recovery_update",
        resource="orders-incident-report",
        intent_digest=intent_digest(),
    )


def test_verified_session_and_exact_grant_admit_the_effect_request():
    receipt = authorize_effect(
        session(),
        grant(),
        effect(),
        expected_audience=AUDIENCE,
        now=NOW,
    )

    assert receipt.subject == "person-204"
    assert receipt.grant_id == "grant-orders-recovery-publish"
    assert receipt.intent_digest == intent_digest()


def test_unverified_session_claims_are_not_identity_evidence():
    unverified = replace(verification(), signature_verified=False)

    with pytest.raises(AuthorityRefused, match="session_not_cryptographically_verified"):
        verify_session(
            claims(),
            unverified,
            expected_issuer=ISSUER,
            expected_audience=AUDIENCE,
            now=NOW,
        )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("issuer", "https://other.example.invalid", "session_issuer_mismatch"),
        ("audience", "billing-console", "session_audience_mismatch"),
        ("expires_at", NOW, "session_expired"),
    ),
)
def test_session_verification_checks_issuer_audience_and_expiry(field, value, reason):
    changed = replace(claims(), **{field: value})

    with pytest.raises(AuthorityRefused, match=reason):
        verify_session(
            changed,
            verification(),
            expected_issuer=ISSUER,
            expected_audience=AUDIENCE,
            now=NOW,
        )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("subject", "person-999", "grant_subject_mismatch"),
        ("session_id", "session-999", "grant_session_mismatch"),
        ("audience", "billing-console", "grant_audience_mismatch"),
        ("operation", "cancel_migration", "grant_operation_mismatch"),
        ("resource", "payments-incident-report", "grant_resource_mismatch"),
        ("intent_digest", "0" * 64, "grant_intent_mismatch"),
        ("expires_at", NOW, "grant_not_current"),
    ),
)
def test_grant_scope_is_exact(field, value, reason):
    changed = replace(grant(), **{field: value})

    with pytest.raises(AuthorityRefused, match=reason):
        authorize_effect(
            session(),
            changed,
            effect(),
            expected_audience=AUDIENCE,
            now=NOW,
        )


def test_rejected_approval_cannot_be_rescued_by_a_valid_grant():
    with pytest.raises(AuthorityRefused, match="approval_not_approved"):
        authorize_effect(
            session(),
            grant(),
            replace(effect(), approval_status="rejected"),
            expected_audience=AUDIENCE,
            now=NOW,
        )


def test_authorization_receipt_still_performs_no_outside_effect():
    receipt = authorize_effect(
        session(),
        grant(),
        effect(),
        expected_audience=AUDIENCE,
        now=NOW,
    )

    assert not hasattr(receipt, "effect_result")

