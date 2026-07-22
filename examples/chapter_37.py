"""Chapter 37: launch only when every independent risk proof exists."""
from orders_investigation.platform.risk import LaunchEvidence, RiskTier, approve_launch

tier = RiskTier("consequential", "bounded-write", True, 100)
denied = approve_launch(tier, LaunchEvidence(90, 1, False, False, False, False)); allowed = approve_launch(tier, LaunchEvidence(140, 0, True, True, True, True))
print("CHAPTER 37 — EXECUTABLE LAUNCH RISK")
print("incomplete evidence", denied, "complete evidence", allowed)
