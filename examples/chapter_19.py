"""Verify identity, then bind one exact delegated grant."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

from orders_investigation.governance.authority import (
    AuthorizedEffect,
    AuthorityRefused,
    DelegatedGrant,
    SessionClaims,
    VerificationEvidence,
    authorize_effect,
    verify_session,
)
from orders_investigation.presentation import chapter_presentation

def main() -> None:
    demo = chapter_presentation(19, description=__doc__)
    now = datetime(2026, 7, 21, 16, 5, tzinfo=timezone.utc)
    issuer = "https://login.example.invalid"
    audience = "orders-investigation"
    digest = "a" * 64
    session = verify_session(
        SessionClaims(issuer, "person-204", audience, "session-551", now + timedelta(minutes=20)),
        VerificationEvidence(True, True),
        expected_issuer=issuer,
        expected_audience=audience,
        now=now,
    )
    grant = DelegatedGrant(
        "grant-orders-report",
        session.subject,
        session.session_id,
        audience,
        "publish_recovery_update",
        "orders-incident-report",
        digest,
        now - timedelta(minutes=1),
        now + timedelta(minutes=10),
    )
    effect = AuthorizedEffect(
        "approval-orders-recovery",
        "approved",
        "publish_recovery_update",
        "orders-incident-report",
        digest,
    )
    receipt = authorize_effect(
        session, grant, effect, expected_audience=audience, now=now
    )
    demo.scenario(1, "Verified identity matches one exact delegated grant")
    demo.fields(
        (
            ("Subject", receipt.subject),
            ("Grant", receipt.grant_id),
            ("Operation", receipt.operation),
            ("Resource", effect.resource),
        ),
        style="evidence",
    )
    demo.decision(True, approved_label="EFFECT AUTHORIZED")
    try:
        authorize_effect(
            session,
            replace(grant, operation="cancel_migration"),
            effect,
            expected_audience=audience,
            now=now,
        )
    except AuthorityRefused as error:
        demo.scenario(2, "Changing the delegated operation breaks the proof")
        demo.decision(False, refused_label="AUTHORITY REFUSED", reason=str(error))
    demo.notice(
        "Identity proves who is present. The grant separately proves what this "
        "session may do to this resource for this approved intent."
    )


if __name__ == "__main__":
    main()
