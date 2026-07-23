import subprocess
import sys

import pytest

from orders_investigation.platform.risk import LaunchEvidence, RiskTier, approve_launch
from orders_investigation.runtime.journey import (
    orders_conformance_receipt,
    orders_data_boundary,
    orders_delegation,
    orders_lifecycle_ownership,
    run_orders_launch,
)


INDEPENDENT_REFUSALS = (
    ("insufficient_evaluation_cases", {"faults": ()}),
    (
        "safety_failure_budget_exceeded",
        {"faults": ("none", "stale_evidence")},
    ),
    (
        "owner_missing",
        {"ownership": orders_lifecycle_ownership(owner="")},
    ),
    (
        "rollback_unproven",
        {
            "receipt": orders_conformance_receipt(
                passed_checks=frozenset(
                    {"trace", "policy", "authority", "placement"}
                )
            )
        },
    ),
    (
        "caller_authority_unproven",
        {"delegation": orders_delegation(action="refund.issue")},
    ),
    (
        "data_boundary_unproven",
        {"boundary": orders_data_boundary(region="us-east-1")},
    ),
)


@pytest.mark.parametrize(("expected_reason", "launch_inputs"), INDEPENDENT_REFUSALS)
def test_launch_path_preserves_each_independent_veto(
    expected_reason,
    launch_inputs,
):
    denied = run_orders_launch(**launch_inputs)

    assert denied.decision == (False, (expected_reason,))
    assert denied.execution is None


def test_complete_launch_evidence_is_admitted():
    tier = RiskTier("consequential", "bounded-write", True, 100)
    assert approve_launch(tier, LaunchEvidence(140, 0, True, True, True, True)) == (True, ())


def test_complete_orders_proof_chain_launches_and_executes_one_spine():
    launched = run_orders_launch()

    assert launched.evidence == LaunchEvidence(4, 0, True, True, True, True)
    assert launched.decision == (True, ())
    assert launched.execution is not None
    assert launched.execution.registered.journey.completed is True
    assert tuple(step.kind for step in launched.execution.registered.journey.steps) == (
        "observe", "decide", "observe", "effect"
    )


def test_demo_shows_each_refused_candidate_stopping_before_execution():
    completed = subprocess.run(
        [sys.executable, "examples/chapter_37.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "THE SYSTEM WE BUILT" in completed.stdout
    assert "1. Bounded investigation" in completed.stdout
    assert "5. Governed evolution" in completed.stdout
    assert "identified → capability admitted → scaffolded" in completed.stdout
    assert "✓ LAUNCH APPROVED" in completed.stdout
    assert "✓ Orders report written once" in completed.stdout
    for expected_reason, _ in INDEPENDENT_REFUSALS:
        assert f"{expected_reason} · NOT EXECUTED" in completed.stdout
