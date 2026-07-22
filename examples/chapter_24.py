"""Chapter 24: real Orders trajectories decide whether a release advances."""

from orders_investigation.runtime.journey import gate_orders_release, run_orders_investigation


accepted = run_orders_investigation()
refused = run_orders_investigation(evidence_current=False)
print("CHAPTER 24 — RELEASE GATE")
print("accepted campaign", gate_orders_release((accepted,)))
print("campaign with refusal", gate_orders_release((accepted, refused)))
