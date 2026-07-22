package orders.report

import rego.v1

default decision := {
    "allow": false,
    "rule_id": "default_deny",
    "obligations": [],
}

decision := {
    "allow": true,
    "rule_id": "publish_recovery_after_current_authorized_evidence",
    "obligations": [
        "attach_supporting_evidence",
        "recheck_authorization_at_effect",
        "record_policy_version",
    ],
} if {
    input.service == "orders"
    input.environment == "production"
    input.operation == "publish_recovery_update"
    input.resource == "orders-incident-report"
    input.approval_status == "approved"
    input.authorization_admitted == true
    input.evidence_current == true
    input.customer_impact_state == "recovered"
}
