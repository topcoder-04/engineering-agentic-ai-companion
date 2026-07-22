import pytest
from orders_investigation.platform.identity import AgentRegistry
from chapter_late_fixtures import contract
from orders_investigation.runtime.journey import (
    orders_agent_contract,
    run_registered_orders_investigation,
)


def test_registry_resolves_exact_immutable_version():
    registry = AgentRegistry(); original = contract(); registry.register(original)
    assert registry.resolve(original.agent_id, original.version) == original
    changed = type(original)(**{**original.__dict__, "owner": "unknown"})
    with pytest.raises(ValueError, match="immutable_version_conflict"):
        registry.register(changed)


def test_orders_investigation_cannot_start_without_exact_registered_identity():
    registry = AgentRegistry()
    registry.register(orders_agent_contract())

    assert run_registered_orders_investigation(registry).journey.completed is True
    with pytest.raises(ValueError, match="agent_version_unknown"):
        run_registered_orders_investigation(registry, version="2")
