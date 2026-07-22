from orders_investigation.operations.probes import variation_matrix
from orders_investigation.runtime.journey import run_orders_variations


def test_probe_matrix_crosses_models_faults_and_timing():
    rows = variation_matrix(["small", "large"], ["none", "timeout"], [0, 500])
    assert len(rows) == 8 and len({row.variation_id for row in rows}) == 8


def test_probe_identifiers_are_reproducible():
    args = (["small"], ["none", "timeout"], [0])
    assert variation_matrix(*args) == variation_matrix(*args)


def test_variations_execute_the_orders_path_and_expose_the_stale_evidence_gap():
    runs = run_orders_variations()
    stable = [run for run in runs if run.variation.dependency_fault == "none"]
    stale = [run for run in runs if run.variation.dependency_fault == "stale_evidence"]

    assert len(runs) == 8
    assert all(run.journey.completed and run.evaluation.passed for run in stable)
    assert all(not run.journey.completed and not run.evaluation.passed for run in stale)
    assert {run.journey.refusal for run in stale} == {
        "current_policy_denied:evidence_current_mismatch"
    }
