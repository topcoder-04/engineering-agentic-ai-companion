"""Chapter 29: register an immutable agent identity."""
from orders_investigation.platform.identity import AgentContract, AgentRegistry

contract = AgentContract("orders", "1", "orders-oncall", "goal/v1", "trace/v2", ("db.read/v2",), "policy/v3", "restricted", frozenset({"restricted"}))
registry = AgentRegistry(); digest = registry.register(contract)
print("CHAPTER 29 — AGENT IDENTITY")
print("resolved", registry.resolve("orders", "1").owner, "manifest", digest[:12])
