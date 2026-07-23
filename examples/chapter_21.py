"""Execute the exact effect and show three guardrail-owned refusals."""

import sqlite3
from dataclasses import replace

from orders_investigation.effects.enforcement import (
    EffectCommand,
    EffectContext,
    EnforcedReportStore,
    GuardrailRefused,
)
from orders_investigation.governance.approval import ApprovalIntent
from orders_investigation.governance.policy import PolicyFacts, orders_report_policy
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(21, description=__doc__)
    intent = ApprovalIntent(
        "publish_recovery_update",
        "orders-incident-report",
        "Order completion recovered; mark customer impact resolved.",
        ("writer-recovery-17", "orders-recovery-17"),
    )
    facts = PolicyFacts(
        "orders",
        "production",
        "publish_recovery_update",
        "orders-incident-report",
        "approved",
        True,
        True,
        "recovered",
    )
    policy = orders_report_policy()
    command = EffectCommand(
        "report-effect-orders-recovery",
        "publish_recovery_update",
        "orders-incident-report",
        intent.content,
        intent.digest,
        7,
        policy.decide(facts),
        (
            "attach_supporting_evidence",
            "recheck_authorization_at_effect",
            "record_policy_version",
        ),
        intent.supporting_evidence,
    )

    def store() -> EnforcedReportStore:
        report = EnforcedReportStore(sqlite3.connect(":memory:"))
        report.seed_report("orders-incident-report", 7, "Investigating recovery.")
        report.activate_policy("orders-report-v1")
        return report

    accepted_store = store()
    receipt = accepted_store.apply(command, EffectContext(facts, intent.digest), policy)
    demo.scenario(1, "Every guard is current at the report write")
    demo.fields(
        (
            ("Effect id", receipt.effect_id),
            ("Policy version", receipt.policy_version),
            (
                "Resource version",
                f"{receipt.previous_resource_version} → {receipt.current_resource_version}",
            ),
        ),
        style="evidence",
    )
    demo.execution(True, "approved report update committed")
    cases = (
        ("direct bypass", replace(command, policy_decision=None), facts),
        ("stale policy", command, facts),
        ("changed current facts", command, replace(facts, evidence_current=False)),
    )
    demo.scenario(2, "The effect boundary owns three independent refusals")
    for label, candidate, current_facts in cases:
        refused_store = store()
        if label == "stale policy":
            refused_store.activate_policy("orders-report-v2")
        try:
            refused_store.apply(
                candidate,
                EffectContext(current_facts, intent.digest),
                policy,
            )
        except GuardrailRefused as error:
            demo.result_row(
                label,
                accepted=False,
                outcome="WRITE REFUSED",
                detail=f"{error} · report remains version 7",
            )
    demo.notice(
        "The write boundary does not trust an earlier approval or policy result. "
        "It rechecks current facts, policy, intent, and resource version itself."
    )


if __name__ == "__main__":
    main()
