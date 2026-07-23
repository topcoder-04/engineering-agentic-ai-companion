from orders_investigation.platform.releases import ConformanceReceipt, release_conforms
from chapter_late_fixtures import contract
import pytest
from orders_investigation.runtime.journey import (
    orders_conformance_receipt,
    run_conformant_orders_investigation,
)


def test_conformance_receipt_is_bound_to_candidate_contract_and_suite():
    current = contract()
    receipt = ConformanceReceipt("candidate-a", current.manifest_digest, "suite-5", frozenset({"trace", "policy"}), frozenset())
    assert release_conforms(
        "candidate-a",
        current,
        receipt,
        {"trace", "policy"},
        required_suite_version="suite-5",
    ) == (True, ())
    assert release_conforms(
        "candidate-b",
        current,
        receipt,
        {"trace", "policy"},
        required_suite_version="suite-5",
    )[1] == ("candidate_evidence_mismatch",)
    assert release_conforms(
        "candidate-a",
        current,
        receipt,
        {"trace", "policy"},
        required_suite_version="suite-6",
    )[1] == ("suite_version_mismatch",)


def test_different_candidate_cannot_reuse_orders_conformance_to_run():
    receipt = orders_conformance_receipt()
    accepted = run_conformant_orders_investigation("candidate-orders-v1", receipt)
    assert accepted.registered.journey.completed is True

    with pytest.raises(
        ValueError,
        match="conformance_refused:candidate_evidence_mismatch",
    ):
        run_conformant_orders_investigation("candidate-orders-v2", receipt)
