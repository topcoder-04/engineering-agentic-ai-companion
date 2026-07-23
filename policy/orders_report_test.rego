package orders.report_test

import data.orders.report
import rego.v1

allow_input := {
    "service": "orders",
    "environment": "production",
    "operation": "publish_recovery_update",
    "resource": "orders-incident-report",
    "approval_status": "approved",
    "authorization_admitted": true,
    "evidence_current": true,
    "customer_impact_state": "recovered",
}

test_exact_input_allows if {
    result := report.decision with input as allow_input
    result.allow
    result.rule_id == "publish_recovery_after_current_authorized_evidence"
    "recheck_authorization_at_effect" in result.obligations
}

test_changed_evidence_denies if {
    changed := object.union(allow_input, {"evidence_current": false})
    result := report.decision with input as changed
    not result.allow
    result.rule_id == "default_deny"
}
