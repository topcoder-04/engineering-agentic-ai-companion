from orders_investigation.platform.capabilities import CapabilityProfile, admit_contract
from chapter_late_fixtures import contract
import pytest
from orders_investigation.platform.identity import AgentRegistry
from orders_investigation.runtime.journey import (
    orders_agent_contract,
    orders_capability_profile,
    run_capability_admitted_orders_investigation,
)


def test_capability_admission_reports_every_incompatible_boundary():
    profile = CapabilityProfile("read-only", frozenset({"balanced"}), frozenset({"catalog.read/v1"}),
                                frozenset({"readonly/v2"}), frozenset({"internal"}))
    assert admit_contract(contract(), profile) == ("model_profile_not_approved", "tool_contract_not_approved",
                                                    "policy_bundle_not_approved", "data_class_not_approved")


def test_incompatible_capability_contract_cannot_run_orders_investigation():
    registry = AgentRegistry()
    registry.register(orders_agent_contract())
    assert run_capability_admitted_orders_investigation(
        registry, orders_capability_profile()
    ).journey.completed is True

    incompatible = CapabilityProfile(
        "read-only",
        frozenset({"reasoning-restricted"}),
        frozenset({"catalog.read/v1"}),
        frozenset({"consequential/v4"}),
        frozenset({"restricted"}),
    )
    with pytest.raises(ValueError, match="capability_refused:tool_contract_not_approved"):
        run_capability_admitted_orders_investigation(registry, incompatible)
