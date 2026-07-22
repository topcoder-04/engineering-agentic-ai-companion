"""Chapter 33: scaffold the safe path and expose overrides."""
from orders_investigation.runtime.journey import run_scaffolded_orders_investigation

accepted = run_scaffolded_orders_investigation()
print("CHAPTER 33 — SAFE DEFAULTS")
print("paved path completed", accepted.registered.journey.completed)
try:
    run_scaffolded_orders_investigation(overrides={"custom/router.py": "# owned"})
except ValueError as exc:
    print("unapproved override refused", exc)
