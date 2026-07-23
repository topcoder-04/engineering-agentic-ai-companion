from orders_investigation.decisions.budget import AttemptOutcome, DecisionBudget, DecisionLedger, ModelAttempt, obtain_choice
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(6, description=__doc__)
    ledger = DecisionLedger(DecisionBudget(max_retries=1))
    result = obtain_choice(
        lambda timeout: ModelAttempt(AttemptOutcome.TIMEOUT, timeout),
        ledger,
    )
    demo.scenario(1, "The model times out and consumes its retry budget")
    demo.fields(
        (
            ("Attempts recorded", len(ledger.attempts)),
            ("Elapsed", f"{ledger.total_elapsed_ms:,} ms"),
            ("Choice returned", result.choice),
            ("Stop reason", result.stop_reason),
        ),
        style="evidence",
    )
    demo.decision(False, refused_label="NO DECISION AVAILABLE", reason=result.stop_reason)
    demo.notice(
        "Timeout attempts remain visible and consume the same run budget. "
        "Exhaustion returns no choice rather than inventing a fallback action."
    )


if __name__ == "__main__":
    main()
