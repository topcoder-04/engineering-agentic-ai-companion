import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from orders_investigation.governance.approval import (
    ApprovalDecision,
    ApprovalIntent,
    ApprovalRefused,
    ApprovalRequest,
    ApprovalSignal,
    ApprovalStatus,
    ApprovalStore,
)


NOW = datetime(2026, 7, 21, 16, 0, tzinfo=timezone.utc)


def intent():
    return ApprovalIntent(
        operation="publish_recovery_update",
        target="orders-incident-report",
        content="Order completion recovered; mark customer impact resolved.",
        supporting_evidence=("writer-recovery-17", "orders-recovery-17"),
    )


def request():
    return ApprovalRequest(
        approval_id="approval-run-1077-recovery-1",
        run_id="run-1077",
        plan_version=2,
        proposal_id="prepare-recovery-update",
        intent=intent(),
        requested_at=NOW,
        expires_at=NOW + timedelta(minutes=30),
    )


def signal(
    decision=ApprovalDecision.APPROVE,
    *,
    signal_id="approval-signal-1",
    intent_digest=None,
    observed_at=NOW + timedelta(minutes=5),
):
    return ApprovalSignal(
        signal_id=signal_id,
        approval_id=request().approval_id,
        intent_digest=intent_digest or intent().digest,
        decision=decision,
        observed_at=observed_at,
    )


def test_wait_and_exact_intent_survive_connection_close_and_reopen(tmp_path):
    path = tmp_path / "approval.sqlite"
    first = sqlite3.connect(path)
    ApprovalStore(first).create(request())
    first.close()

    second = sqlite3.connect(path)
    restored = ApprovalStore(second).load(request().approval_id)
    second.close()

    assert restored.status == ApprovalStatus.WAITING
    assert restored.request.intent == intent()
    assert restored.request.intent.digest == intent().digest


def test_exact_signal_approves_the_waiting_intent():
    store = ApprovalStore(sqlite3.connect(":memory:"))
    store.create(request())

    receipt = store.deliver(signal())

    assert receipt.status == ApprovalStatus.APPROVED
    assert receipt.intent_digest == intent().digest
    assert store.load(request().approval_id).decision_signal_id == "approval-signal-1"


def test_rejection_is_a_durable_terminal_decision():
    store = ApprovalStore(sqlite3.connect(":memory:"))
    store.create(request())

    store.deliver(signal(ApprovalDecision.REJECT))

    assert store.load(request().approval_id).status == ApprovalStatus.REJECTED
    with pytest.raises(ApprovalRefused, match="approval_already_decided"):
        store.deliver(signal(signal_id="later-approval"))


def test_signal_for_changed_intent_is_refused_and_wait_remains():
    store = ApprovalStore(sqlite3.connect(":memory:"))
    store.create(request())

    with pytest.raises(ApprovalRefused, match="approval_intent_mismatch"):
        store.deliver(signal(intent_digest="0" * 64))

    assert store.load(request().approval_id).status == ApprovalStatus.WAITING


def test_exact_duplicate_signal_returns_the_stored_decision():
    store = ApprovalStore(sqlite3.connect(":memory:"))
    store.create(request())
    first = store.deliver(signal())

    duplicate = store.deliver(signal())

    assert first.duplicate is False
    assert duplicate.duplicate is True
    assert duplicate.status == ApprovalStatus.APPROVED


def test_reused_signal_id_with_changed_payload_is_refused():
    store = ApprovalStore(sqlite3.connect(":memory:"))
    store.create(request())
    store.deliver(signal())
    changed = signal(ApprovalDecision.REJECT)

    with pytest.raises(ApprovalRefused, match="approval_signal_conflict"):
        store.deliver(changed)


def test_late_signal_expires_the_wait_instead_of_approving():
    store = ApprovalStore(sqlite3.connect(":memory:"))
    store.create(request())

    with pytest.raises(ApprovalRefused, match="approval_expired"):
        store.deliver(signal(observed_at=NOW + timedelta(minutes=31)))

    assert store.load(request().approval_id).status == ApprovalStatus.EXPIRED


def test_unknown_approval_id_cannot_be_created_by_a_signal():
    store = ApprovalStore(sqlite3.connect(":memory:"))
    unknown = ApprovalSignal(
        signal_id="orphan-signal",
        approval_id="missing-approval",
        intent_digest=intent().digest,
        decision=ApprovalDecision.APPROVE,
        observed_at=NOW,
    )

    with pytest.raises(ApprovalRefused, match="approval_request_unknown"):
        store.deliver(unknown)


def test_approval_record_does_not_claim_who_decided_or_what_they_may_decide():
    record = ApprovalStore(sqlite3.connect(":memory:"))
    stored = record.create(request())

    assert set(stored.__dict__) == {"request", "status", "decision_signal_id"}

