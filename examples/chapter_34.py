"""Chapter 34: bind release evidence to the exact artifact."""
from orders_investigation.runtime.journey import (
    orders_conformance_receipt,
    run_conformant_orders_investigation,
)
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(34, description=__doc__)
    receipt = orders_conformance_receipt()
    accepted = run_conformant_orders_investigation("candidate-orders-v1", receipt)
    demo.scenario(1, "Passing evidence stays bound to the exact candidate")
    demo.fields(
        (
            ("Candidate digest", receipt.candidate_digest),
            ("Checks", ", ".join(sorted(receipt.passed_checks))),
            ("Journey completed", accepted.registered.journey.completed),
        ),
        style="evidence",
    )
    demo.decision(True, approved_label="CONFORMANCE PROVEN")
    demo.scenario(2, "Another artifact cannot reuse the receipt")
    try:
        run_conformant_orders_investigation("candidate-orders-v2", receipt)
    except ValueError as exc:
        demo.decision(False, refused_label="RECEIPT REFUSED", reason=str(exc))
    demo.notice(
        "The receipt binds candidate, contract, suite, and checks. Passing proof "
        "cannot be detached and replayed against a different artifact."
    )


if __name__ == "__main__":
    main()
