"""Show that wording is absent from the structured policy decision."""

from dataclasses import replace

from orders_investigation.governance.policy import PolicyFacts, orders_report_policy
from orders_investigation.presentation import chapter_presentation

def main() -> None:
    demo = chapter_presentation(20, description=__doc__)
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
    requests = (
        "Publish the Orders recovery update.",
        "Customer impact is over; please post the resolution note.",
    )
    decisions = tuple(orders_report_policy().decide(facts) for _ in requests)
    demo.scenario(1, "Different wording produces the same fact decision")
    for index, (request, decision) in enumerate(zip(requests, decisions), start=1):
        demo.result_row(
            f"Wording {index}",
            accepted=decision.allow,
            outcome=f"ALLOW · {decision.rule_id}",
            detail=request,
        )
    demo.fields((("Request text is a policy fact", hasattr(facts, "request_text")),))
    denied = orders_report_policy().decide(replace(facts, evidence_current=False))
    demo.scenario(2, "One structured fact changes")
    demo.decision(
        denied.allow,
        refused_label="POLICY REFUSED",
        reason=", ".join(denied.reasons),
    )
    demo.notice(
        "Policy evaluates typed current facts, not the persuasiveness of request "
        "text. Equivalent meaning stays equivalent; changed evidence does not."
    )


if __name__ == "__main__":
    main()
