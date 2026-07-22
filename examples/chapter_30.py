"""Chapter 30: admit only compatible capabilities."""
from orders_investigation.platform.capabilities import CapabilityProfile
from orders_investigation.platform.identity import AgentRegistry
from orders_investigation.runtime.journey import (
    orders_agent_contract,
    orders_capability_profile,
    run_capability_admitted_orders_investigation,
)

registry = AgentRegistry()
registry.register(orders_agent_contract())
accepted = run_capability_admitted_orders_investigation(
    registry, orders_capability_profile()
)
print("CHAPTER 30 — CAPABILITY ADMISSION")
print("accepted", accepted.journey.completed)
try:
    run_capability_admitted_orders_investigation(
        registry,
        CapabilityProfile("read-only", frozenset(), frozenset(), frozenset(), frozenset()),
    )
except ValueError as exc:
    print("incompatible profile refused", exc)
