from orders_investigation.decisions.routing import (
    CostClass,
    DataClass,
    JudgmentRequirements,
    LatencyClass,
    choose_judgment_source,
    orders_model_profiles,
)


def test_low_cost_task_choice_uses_the_first_matching_profile():
    decision = choose_judgment_source(
        JudgmentRequirements(
            capability="task_choice",
            max_cost_class=CostClass.LOW,
            max_latency_class=LatencyClass.LOW,
            data_class=DataClass.STANDARD,
        ),
        orders_model_profiles(),
    )
    assert decision.selected.source_id == "quick-choice"
    assert decision.used_fallback is False


def test_generated_analysis_skips_a_profile_without_the_capability():
    decision = choose_judgment_source(
        JudgmentRequirements(
            capability="generated_analysis",
            max_cost_class=CostClass.MEDIUM,
            max_latency_class=LatencyClass.MEDIUM,
            data_class=DataClass.STANDARD,
        ),
        orders_model_profiles(),
    )
    assert decision.selected.source_id == "deeper-choice"
    assert decision.evaluations[0].reason == "capability_missing"


def test_restricted_data_reaches_only_a_profile_that_accepts_it():
    decision = choose_judgment_source(
        JudgmentRequirements(
            capability="generated_analysis",
            max_cost_class=CostClass.HIGH,
            max_latency_class=LatencyClass.HIGH,
            data_class=DataClass.RESTRICTED,
        ),
        orders_model_profiles(),
    )
    assert decision.selected.source_id == "private-analysis"
    assert [item.reason for item in decision.evaluations] == [
        "capability_missing",
        "data_rule_not_met",
        "requirements_met",
    ]


def test_unavailable_preferred_source_uses_only_an_eligible_fallback():
    decision = choose_judgment_source(
        JudgmentRequirements(
            capability="task_choice",
            max_cost_class=CostClass.MEDIUM,
            max_latency_class=LatencyClass.MEDIUM,
            data_class=DataClass.STANDARD,
        ),
        orders_model_profiles(),
        unavailable=frozenset({"quick-choice"}),
    )
    assert decision.selected.source_id == "deeper-choice"
    assert decision.used_fallback is True


def test_no_source_is_better_than_violating_a_data_rule():
    decision = choose_judgment_source(
        JudgmentRequirements(
            capability="generated_analysis",
            max_cost_class=CostClass.MEDIUM,
            max_latency_class=LatencyClass.MEDIUM,
            data_class=DataClass.RESTRICTED,
        ),
        orders_model_profiles(),
    )
    assert decision.selected is None
    assert decision.used_fallback is False
    assert decision.evaluations[-1].reason == "cost_ceiling_exceeded"


def test_configured_classes_are_policy_inputs_not_observed_measurements():
    profiles = orders_model_profiles()
    assert profiles[0].model_id == "configured-quick-model"
    assert all("observed" not in profile.model_id for profile in profiles)

