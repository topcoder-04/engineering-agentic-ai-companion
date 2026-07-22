from orders_investigation.operations.probes import variation_matrix


def test_probe_matrix_crosses_models_faults_and_timing():
    rows = variation_matrix(["small", "large"], ["none", "timeout"], [0, 500])
    assert len(rows) == 8 and len({row.variation_id for row in rows}) == 8


def test_probe_identifiers_are_reproducible():
    args = (["small"], ["none", "timeout"], [0])
    assert variation_matrix(*args) == variation_matrix(*args)
