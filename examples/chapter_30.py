"""Chapter 30: admit only compatible capabilities."""
from orders_investigation.platform.capabilities import CapabilityProfile, admit_contract
from orders_investigation.platform.identity import AgentContract

contract = AgentContract("orders", "1", "orders-oncall", "goal/v1", "trace/v2", ("db.read/v2",), "policy/v3", "restricted", frozenset({"restricted"}))
profile = CapabilityProfile("read-only", frozenset({"restricted"}), frozenset({"db.read/v2"}), frozenset({"policy/v3"}), frozenset({"restricted"}))
print("CHAPTER 30 — CAPABILITY ADMISSION")
print("refusal reasons", admit_contract(contract, profile))
