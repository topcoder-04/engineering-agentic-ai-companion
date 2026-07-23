"""Chapter 26: execute the Orders journey across deliberate variations."""

from orders_investigation.runtime.journey import run_orders_variations
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(26, description=__doc__)
    runs = run_orders_variations()
    passed = [run for run in runs if run.evaluation.passed]
    refused = [run for run in runs if run.journey.refusal]
    demo.scenario(1, "The real Orders journey runs across deliberate variation")
    demo.fields(
        (
            ("Variations executed", len(runs)),
            ("Passed", len(passed)),
            ("Refused", len(refused)),
        ),
        style="evidence",
    )
    demo.scenario(2, "Stale evidence exposes the hidden boundary")
    demo.fields(
        (
            ("Variation", refused[0].variation.variation_id),
            ("Refusal", refused[0].journey.refusal),
        )
    )
    demo.decision(False, refused_label="VARIATION FAILED AS EXPECTED")
    demo.notice(
        "The campaign changes model, dependency, and timing conditions while "
        "executing the same production path. Robustness is observed, not assumed."
    )


if __name__ == "__main__":
    main()
