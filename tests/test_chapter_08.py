import sqlite3

from orders_investigation.effects.idempotency import (
    EffectIntent,
    IdempotencyConflict,
    ReportEffectService,
    ResponseLost,
    report_update_intent,
)


def test_lost_response_and_exact_retry_produce_one_effect(tmp_path):
    path = tmp_path / "report-effects.sqlite"
    first = sqlite3.connect(path)
    service = ReportEffectService(first)
    intent = report_update_intent()
    key = "report-update:run-1042:1"

    try:
        service.apply(intent, idempotency_key=key, lose_response=True)
    except ResponseLost as exc:
        assert str(exc) == "response_lost_after_effect_commit"
    else:
        raise AssertionError("the first response should be lost")
    first.close()

    second = sqlite3.connect(path)
    restored_service = ReportEffectService(second)
    retry = restored_service.apply(intent, idempotency_key=key)
    assert retry.status == "applied"
    assert retry.replayed
    assert restored_service.effect_count == 1
    second.close()


def test_same_key_with_changed_intent_is_rejected(tmp_path):
    connection = sqlite3.connect(tmp_path / "intent-conflict.sqlite")
    service = ReportEffectService(connection)
    key = "report-update:run-1042:1"
    service.apply(report_update_intent(), idempotency_key=key)

    changed = EffectIntent(
        operation="update_report",
        target="incident_report",
        content="Cancel the migration and mark the incident resolved.",
    )
    try:
        service.apply(changed, idempotency_key=key)
    except IdempotencyConflict as exc:
        assert str(exc) == "idempotency_key_reused_for_different_intent"
    else:
        raise AssertionError("changed intent must not reuse the key")
    assert service.effect_count == 1
    connection.close()


def test_changing_the_key_can_duplicate_the_same_intent(tmp_path):
    connection = sqlite3.connect(tmp_path / "unstable-key.sqlite")
    service = ReportEffectService(connection)
    intent = report_update_intent()
    service.apply(intent, idempotency_key="report-update:run-1042:1")
    service.apply(intent, idempotency_key="report-update:run-1042:retry")
    assert service.effect_count == 2
    connection.close()


