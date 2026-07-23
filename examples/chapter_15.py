"""Route four decision shapes without violating their requirements."""

from orders_investigation.decisions.routing import (
    CostClass,
    DataClass,
    JudgmentRequirements,
    LatencyClass,
    choose_judgment_source,
    orders_model_profiles,
)
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(15, description=__doc__)
    cases = (
        (
            "ordinary task choice",
            JudgmentRequirements("task_choice", CostClass.LOW, LatencyClass.LOW, DataClass.STANDARD),
        ),
        (
            "generated analysis",
            JudgmentRequirements(
                "generated_analysis",
                CostClass.MEDIUM,
                LatencyClass.MEDIUM,
                DataClass.STANDARD,
            ),
        ),
        (
            "restricted analysis",
            JudgmentRequirements(
                "generated_analysis",
                CostClass.HIGH,
                LatencyClass.HIGH,
                DataClass.RESTRICTED,
            ),
        ),
        (
            "restricted under medium ceiling",
            JudgmentRequirements(
                "generated_analysis",
                CostClass.MEDIUM,
                LatencyClass.MEDIUM,
                DataClass.RESTRICTED,
            ),
        ),
    )
    demo.scenario(1, "Requirements select the smallest compatible source")
    for label, requirements in cases:
        decision = choose_judgment_source(requirements, orders_model_profiles())
        selected = decision.selected.source_id if decision.selected else "no source"
        demo.result_row(
            label,
            accepted=decision.selected is not None,
            outcome=selected if decision.selected else "NO COMPATIBLE SOURCE",
            detail=(
                f"{requirements.max_cost_class.name.lower()} cost · "
                f"{requirements.max_latency_class.name.lower()} latency · "
                f"{requirements.data_class.value} data"
            ),
        )
    demo.notice(
        "The router does not ask a model where to route. It compares declared "
        "requirements with declared profiles and fails closed when none fit."
    )


if __name__ == "__main__":
    main()
