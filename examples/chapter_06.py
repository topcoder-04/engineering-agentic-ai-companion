from orders_investigation.decisions.budget import AttemptOutcome, DecisionBudget, DecisionLedger, ModelAttempt, obtain_choice

ledger = DecisionLedger(DecisionBudget(max_retries=1))
result = obtain_choice(lambda timeout: ModelAttempt(AttemptOutcome.TIMEOUT, timeout), ledger)
print(f"Attempts: {len(ledger.attempts)}")
print(f"Elapsed: {ledger.total_elapsed_ms} ms")
print(f"Choice: {result.choice}")
print(f"Stop reason: {result.stop_reason}")

