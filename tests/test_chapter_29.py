import pytest
from orders_investigation.platform.identity import AgentRegistry
from chapter_late_fixtures import contract


def test_registry_resolves_exact_immutable_version():
    registry = AgentRegistry(); original = contract(); registry.register(original)
    assert registry.resolve(original.agent_id, original.version) == original
    changed = type(original)(**{**original.__dict__, "owner": "unknown"})
    with pytest.raises(ValueError, match="immutable_version_conflict"):
        registry.register(changed)
