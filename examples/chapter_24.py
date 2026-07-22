"""Chapter 24: a release gate fails closed without evaluation evidence."""
from orders_investigation.evaluation.production import ReleaseThresholds, gate_release

decision = gate_release([], [], ReleaseThresholds(.95))
print("CHAPTER 24 — RELEASE GATE")
print("allowed", decision.allowed, "reasons", decision.reasons)
