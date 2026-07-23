"""Chapter 23: evaluate the path produced by the Orders investigation."""

from orders_investigation.runtime.journey import (
    evaluate_orders_investigation,
    run_orders_investigation,
)
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(23, description=__doc__)
    accepted = evaluate_orders_investigation(run_orders_investigation())
    refused = evaluate_orders_investigation(
        run_orders_investigation(evidence_current=False)
    )
    demo.scenario(1, "The complete Orders path satisfies every dimension")
    demo.fields((("Dimensions", accepted.dimensions),), style="evidence")
    demo.decision(accepted.passed, approved_label="TRAJECTORY PASSED")
    demo.scenario(2, "A useful partial path still fails its outcome contract")
    demo.fields((("Reasons", ", ".join(refused.reasons)),), style="evidence")
    demo.decision(refused.passed, refused_label="TRAJECTORY FAILED")
    demo.notice(
        "The same evaluator judges evidence, path, action, and outcome. Useful "
        "observations cannot compensate for a refused report effect."
    )


if __name__ == "__main__":
    main()
