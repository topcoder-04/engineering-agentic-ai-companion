from dataclasses import replace
from pathlib import Path

import pytest

from orders_investigation.governance.policy import PolicyRule, PolicySet, orders_report_policy
from orders_investigation.governance.policy import PolicyFacts


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


def test_exact_structured_facts_allow_with_explicit_obligations():
    decision = orders_report_policy().decide(facts())

    assert decision.allow is True
    assert decision.policy_version == "orders-report-v1"
    assert decision.obligations == (
        "attach_supporting_evidence",
        "recheck_authorization_at_effect",
        "record_policy_version",
    )


def test_different_wording_cannot_change_the_structured_decision():
    requests = (
        "Publish the Orders recovery update.",
        "Customer impact is over; please post the resolution note.",
    )
    decisions = tuple(orders_report_policy().decide(facts()) for _ in requests)

    assert decisions[0] == decisions[1]
    assert not hasattr(facts(), "request_text")


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("service", "payments", "service_mismatch"),
        ("environment", "staging", "environment_mismatch"),
        ("operation", "cancel_migration", "operation_mismatch"),
        ("resource", "payments-incident-report", "resource_mismatch"),
        ("approval_status", "rejected", "approval_status_mismatch"),
        ("authorization_admitted", False, "authorization_admitted_mismatch"),
        ("evidence_current", False, "evidence_current_mismatch"),
        ("customer_impact_state", "unknown", "customer_impact_state_mismatch"),
    ),
)
def test_one_changed_decisive_fact_denies(field, value, reason):
    decision = orders_report_policy().decide(replace(facts(), **{field: value}))

    assert decision.allow is False
    assert decision.rule_id == "default_deny"
    assert reason in decision.reasons
    assert decision.obligations == ()


def test_policy_version_and_rule_are_part_of_the_decision_receipt():
    decision = orders_report_policy().decide(facts())

    assert decision.policy_version == "orders-report-v1"
    assert decision.rule_id == "publish_recovery_after_current_authorized_evidence"


def test_duplicate_rule_identity_is_refused():
    duplicate = PolicyRule("same", (), ())

    with pytest.raises(ValueError, match="policy_rule_id_repeated"):
        PolicySet("broken", (duplicate, duplicate))


def test_rego_mapping_preserves_the_direct_rule_and_obligations():
    source = Path("policy/orders_report.rego").read_text()

    assert 'input.operation == "publish_recovery_update"' in source
    assert 'input.resource == "orders-incident-report"' in source
    assert '"recheck_authorization_at_effect"' in source
    assert 'default decision := {' in source


def test_rego_mapping_has_success_and_changed_fact_tests():
    source = Path("policy/orders_report_test.rego").read_text()

    assert "test_exact_input_allows" in source
    assert "test_changed_evidence_denies" in source
    assert 'with input as changed' in source

