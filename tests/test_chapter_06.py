from orders_investigation.decisions.budget import (
    AttemptOutcome,
    DecisionBudget,
    DecisionLedger,
    ModelAttempt,
    obtain_choice,
)
from orders_investigation.decisions.model import ModelChoice


def test_successful_call_records_usage_and_choice():
    ledger = DecisionLedger(DecisionBudget())

    def successful_call(timeout_ms):
        assert timeout_ms == 4_000
        return ModelAttempt(
            AttemptOutcome.CHOICE,
            elapsed_ms=820,
            choice=ModelChoice("inspect_pipeline_run", "Find the trigger.", "pipeline record"),
            input_units=740,
            output_units=48,
        )

    result = obtain_choice(successful_call, ledger)
    assert result.choice.task_id == "inspect_pipeline_run"
    assert result.stop_reason is None
    assert ledger.total_input_units == 740
    assert ledger.total_output_units == 48


def test_two_timeouts_record_attempts_and_return_no_choice():
    ledger = DecisionLedger(DecisionBudget(max_retries=1))

    def timeout_call(timeout_ms):
        return ModelAttempt(AttemptOutcome.TIMEOUT, elapsed_ms=timeout_ms)

    result = obtain_choice(timeout_call, ledger)
    assert result.choice is None
    assert result.stop_reason == "model_timeout"
    assert len(ledger.attempts) == 2
    assert ledger.total_elapsed_ms == 8_000


def test_exhausted_budget_refuses_before_call():
    ledger = DecisionLedger(DecisionBudget(max_calls=0))
    called = False

    def should_not_run(timeout_ms):
        nonlocal called
        called = True
        return ModelAttempt(AttemptOutcome.UNAVAILABLE, elapsed_ms=0)

    result = obtain_choice(should_not_run, ledger)
    assert result.stop_reason == "decision_budget_exhausted"
    assert result.choice is None
    assert not called


def test_failed_attempt_cannot_smuggle_in_a_choice():
    ledger = DecisionLedger(DecisionBudget())
    try:
        ledger.record(ModelAttempt(
            AttemptOutcome.TIMEOUT,
            elapsed_ms=4_000,
            choice=ModelChoice("inspect_pipeline_run", "stale", "stale"),
        ))
    except ValueError as exc:
        assert str(exc) == "failed_attempt_cannot_contain_choice"
    else:
        raise AssertionError("timeout accepted a fabricated choice")

