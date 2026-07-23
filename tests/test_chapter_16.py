import sqlite3

import pytest

from orders_investigation.graph.planning import (
    Commitment,
    CommitmentStatus,
    EvidenceReference,
    Plan,
    PlanRefused,
    PlanStore,
    changed_evidence,
)


def initial_plan():
    return Plan(
        run_id="run-1077",
        version=1,
        question="How should the active migration pressure be reduced?",
        evidence_boundary=(
            EvidenceReference("migration_status", "running"),
            EvidenceReference("writer_pressure", "high"),
        ),
        commitments=(
            Commitment("inspect_pipeline_run", CommitmentStatus.SUCCEEDED),
            Commitment("inspect_migration_controls", CommitmentStatus.READY),
            Commitment("propose_throttle_action", CommitmentStatus.WAITING),
        ),
    )


def replacement_plan():
    return Plan(
        run_id="run-1077",
        version=2,
        question="Did Orders recover after the migration completed?",
        evidence_boundary=(
            EvidenceReference("migration_status", "completed"),
            EvidenceReference("writer_pressure", "falling"),
        ),
        commitments=(
            Commitment("inspect_pipeline_run", CommitmentStatus.SUCCEEDED),
            Commitment("confirm_writer_recovery", CommitmentStatus.READY),
            Commitment("confirm_order_recovery", CommitmentStatus.READY),
            Commitment("update_incident_report", CommitmentStatus.WAITING),
        ),
        supersedes_version=1,
    )


def test_changed_evidence_blocks_assuming_the_old_plan_is_current():
    changed = changed_evidence(
        initial_plan(),
        {"migration_status": "completed", "writer_pressure": "falling"},
    )
    assert changed == ("migration_status", "writer_pressure")


def test_replacement_preserves_completed_work_and_supersedes_future_work():
    connection = sqlite3.connect(":memory:")
    store = PlanStore(connection)
    store.create(initial_plan(), {"migration_status": "running", "writer_pressure": "high"})
    receipt = store.replace(
        replacement_plan(),
        {"migration_status": "completed", "writer_pressure": "falling"},
    )
    assert receipt.preserved_succeeded == ("inspect_pipeline_run",)
    assert receipt.superseded_future == (
        "inspect_migration_controls",
        "propose_throttle_action",
    )
    assert store.active("run-1077").version == 2


def test_old_plan_version_cannot_admit_late_future_work():
    connection = sqlite3.connect(":memory:")
    store = PlanStore(connection)
    store.create(initial_plan(), {"migration_status": "running", "writer_pressure": "high"})
    store.replace(
        replacement_plan(),
        {"migration_status": "completed", "writer_pressure": "falling"},
    )
    with pytest.raises(PlanRefused, match="plan_version_not_active"):
        store.require_current("run-1077", 1)


def test_replacement_cannot_remove_succeeded_work():
    connection = sqlite3.connect(":memory:")
    store = PlanStore(connection)
    store.create(initial_plan(), {"migration_status": "running", "writer_pressure": "high"})
    bad = Plan(
        run_id="run-1077",
        version=2,
        question="Did Orders recover?",
        evidence_boundary=(EvidenceReference("migration_status", "completed"),),
        commitments=(Commitment("confirm_order_recovery", CommitmentStatus.READY),),
        supersedes_version=1,
    )
    with pytest.raises(PlanRefused, match="succeeded_commitment_removed"):
        store.replace(bad, {"migration_status": "completed", "writer_pressure": "falling"})


def test_failed_atomic_replacement_leaves_the_previous_plan_active():
    connection = sqlite3.connect(":memory:")
    store = PlanStore(connection)
    store.create(initial_plan(), {"migration_status": "running", "writer_pressure": "high"})
    with pytest.raises(RuntimeError, match="injected_before_plan_commit"):
        store.replace(
            replacement_plan(),
            {"migration_status": "completed", "writer_pressure": "falling"},
            fail_before_commit=True,
        )
    assert store.active("run-1077").version == 1


def test_replacement_requires_an_observed_change():
    connection = sqlite3.connect(":memory:")
    store = PlanStore(connection)
    store.create(initial_plan(), {"migration_status": "running", "writer_pressure": "high"})
    with pytest.raises(PlanRefused, match="evidence_did_not_change"):
        store.replace(
            replacement_plan(),
            {"migration_status": "running", "writer_pressure": "high"},
        )
