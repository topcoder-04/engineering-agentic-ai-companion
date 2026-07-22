from orders_investigation.platform.capabilities import CapabilityProfile, admit_contract
from chapter_late_fixtures import contract


def test_capability_admission_reports_every_incompatible_boundary():
    profile = CapabilityProfile("read-only", frozenset({"balanced"}), frozenset({"catalog.read/v1"}),
                                frozenset({"readonly/v2"}), frozenset({"internal"}))
    assert admit_contract(contract(), profile) == ("model_profile_not_approved", "tool_contract_not_approved",
                                                    "policy_bundle_not_approved", "data_class_not_approved")
