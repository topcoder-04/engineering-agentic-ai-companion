"""Chapter 29: register an immutable agent identity."""
from orders_investigation.platform.identity import AgentRegistry
from orders_investigation.runtime.journey import (
    orders_agent_contract,
    run_registered_orders_investigation,
)

registry = AgentRegistry()
digest = registry.register(orders_agent_contract())
accepted = run_registered_orders_investigation(registry)
print("CHAPTER 29 — AGENT IDENTITY")
print("accepted", accepted.journey.completed, "owner", accepted.contract.owner, "manifest", digest[:12])
try:
    run_registered_orders_investigation(registry, version="2")
except ValueError as exc:
    print("unknown version refused", exc)
