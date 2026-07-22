import sqlite3
from dataclasses import replace

import pytest

from orders_investigation.governance.approval import ApprovalIntent
from orders_investigation.effects.enforcement import (
    EffectCommand,
    EffectContext,
    EnforcedReportStore,
    GuardrailRefused,
)
from orders_investigation.governance.policy import PolicyFacts, orders_report_policy


def digest():
    return ApprovalIntent(
        operation="publish_recovery_update",
        target="orders-incident-report",
        content="Order completion recovered; mark customer impact resolved.",
        supporting_evidence=("writer-recovery-17", "orders-recovery-17"),
    ).digest


def facts():
    return PolicyFacts(
        service="orders",
        environment="production",
        operation="publish_recovery_update",
        resource="orders-incident-report",
        approval_status="approved",
        authorization_admitted=True,
        evidence_current=True,
        customer_impact_state="recovered",
    )


def context(**changes):
    current_facts = replace(facts(), **changes) if changes else facts()
    return EffectContext(current_facts, digest())


def command(**changes):
    policy = orders_report_policy()
    base = EffectCommand(
        effect_id="report-effect-run-1077-recovery",
        operation="publish_recovery_update",
        resource="orders-incident-report",
        content="Order completion recovered; mark customer impact resolved.",
        intent_digest=digest(),
        expected_resource_version=7,
        policy_decision=policy.decide(facts()),
        applied_obligations=(
            "attach_supporting_evidence",
            "recheck_authorization_at_effect",
            "record_policy_version",
        ),
        supporting_evidence=("writer-recovery-17", "orders-recovery-17"),
    )
    return replace(base, **changes) if changes else base


def store():
    result = EnforcedReportStore(sqlite3.connect(":memory:"))
    result.seed_report("orders-incident-report", 7, "Investigating recovery.")
    result.activate_policy("orders-report-v1")
    return result


def test_effect_boundary_rechecks_and_applies_the_exact_command():
    result = store()

    receipt = result.apply(command(), context(), orders_report_policy())

    assert receipt.previous_resource_version == 7
    assert receipt.current_resource_version == 8
    assert receipt.policy_version == "orders-report-v1"
    assert result.report("orders-incident-report") == (
        8,
        "Order completion recovered; mark customer impact resolved.",
    )


def test_direct_adapter_bypass_without_policy_decision_is_refused():
    result = store()

    with pytest.raises(GuardrailRefused, match="policy_decision_missing"):
        result.apply(command(policy_decision=None), context(), orders_report_policy())

    assert result.report("orders-incident-report")[0] == 7


def test_policy_activation_change_refuses_an_old_decision():
    result = store()
    result.activate_policy("orders-report-v2")

    with pytest.raises(GuardrailRefused, match="policy_runtime_not_active"):
        result.apply(command(), context(), orders_report_policy())


def test_current_facts_are_rechecked_after_upstream_allow():
    result = store()

    with pytest.raises(
        GuardrailRefused,
        match="current_policy_denied:evidence_current_mismatch",
    ):
        result.apply(
            command(),
            context(evidence_current=False),
            orders_report_policy(),
        )


@pytest.mark.parametrize(
    "missing",
    (
        "attach_supporting_evidence",
        "recheck_authorization_at_effect",
        "record_policy_version",
    ),
)
def test_every_obligation_must_be_applied(missing):
    result = store()
    applied = tuple(
        item for item in command().applied_obligations if item != missing
    )

    with pytest.raises(GuardrailRefused, match=f"obligation_not_applied:{missing}"):
        result.apply(
            command(applied_obligations=applied),
            context(),
            orders_report_policy(),
        )


def test_evidence_attachment_cannot_be_empty():
    result = store()

    with pytest.raises(GuardrailRefused, match="supporting_evidence_missing"):
        result.apply(
            command(supporting_evidence=()),
            context(),
            orders_report_policy(),
        )


def test_resource_version_race_is_refused_without_overwrite():
    result = store()

    with pytest.raises(GuardrailRefused, match="resource_version_changed"):
        result.apply(
            command(expected_resource_version=6),
            context(),
            orders_report_policy(),
        )

    assert result.report("orders-incident-report")[1] == "Investigating recovery."


def test_changed_intent_cannot_reuse_the_authorized_path():
    result = store()

    with pytest.raises(GuardrailRefused, match="effect_intent_changed"):
        result.apply(
            command(intent_digest="0" * 64),
            context(),
            orders_report_policy(),
        )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("operation", "cancel_migration", "effect_operation_changed"),
        ("resource", "payments-incident-report", "effect_resource_changed"),
    ),
)
def test_effect_shape_cannot_change_after_policy(field, value, reason):
    result = store()

    with pytest.raises(GuardrailRefused, match=reason):
        result.apply(
            command(**{field: value}),
            context(),
            orders_report_policy(),
        )


def test_failed_boundary_check_leaves_no_effect_receipt():
    result = store()
    with pytest.raises(GuardrailRefused):
        result.apply(
            command(expected_resource_version=6),
            context(),
            orders_report_policy(),
        )

    count = result.connection.execute("SELECT count(*) FROM enforced_effects").fetchone()[0]
    assert count == 0
