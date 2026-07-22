from orders_investigation.platform.releases import ConformanceReceipt, release_conforms
from chapter_late_fixtures import contract


def test_conformance_receipt_is_bound_to_candidate_contract_and_suite():
    current = contract()
    receipt = ConformanceReceipt("candidate-a", current.manifest_digest, "suite-5", frozenset({"trace", "policy"}), frozenset())
    assert release_conforms("candidate-a", current, receipt, {"trace", "policy"}) == (True, ())
    assert release_conforms("candidate-b", current, receipt, {"trace", "policy"})[1] == ("candidate_evidence_mismatch",)
