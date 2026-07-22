from orders_investigation.effects.reconciliation import EffectOutcome, failure_before_dispatch

attempt = failure_before_dispatch("report-update:run-1042:1")
print(f"Dispatched: {attempt.dispatched}")
print(f"Effect outcome: {attempt.effect_outcome.value}")
assert attempt.effect_outcome is EffectOutcome.NOT_DISPATCHED

