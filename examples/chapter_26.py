"""Chapter 26: execute the Orders journey across deliberate variations."""

from orders_investigation.runtime.journey import run_orders_variations


runs = run_orders_variations()
passed = [run for run in runs if run.evaluation.passed]
refused = [run for run in runs if run.journey.refusal]
print("CHAPTER 26 — VARIATION MATRIX")
print("executed", len(runs), "passed", len(passed), "refused", len(refused))
print("first refusal", refused[0].variation.variation_id, refused[0].journey.refusal)
