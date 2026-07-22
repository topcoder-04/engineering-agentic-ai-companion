import pytest
from orders_investigation.platform.placement import (
    DataBoundary,
    ExecutionTarget,
    cache_address,
    place,
)
from orders_investigation.runtime.journey import (
    orders_data_boundary,
    orders_execution_targets,
    run_placed_orders_investigation,
)


def test_cache_address_makes_tenant_and_data_boundary_structural():
    search = DataBoundary("search", "restricted", "eu-west-1", 7)
    payments = DataBoundary("payments", "restricted", "eu-west-1", 7)
    assert cache_address(search, "doc-7", "embed-v3") == (
        "search/restricted/eu-west-1/embed-v3/doc-7"
    )
    assert cache_address(payments, "doc-7", "embed-v3") == (
        "payments/restricted/eu-west-1/embed-v3/doc-7"
    )
    with pytest.raises(ValueError, match="invalid_artifact_id"):
        cache_address(search, "../payments/doc-7", "embed-v3")


def test_placement_refuses_every_least_wrong_target():
    boundary = DataBoundary("tenant-a", "restricted", "eu-west-1", 7)
    targets = (ExecutionTarget("wrong-tenant", "tenant-b", frozenset({"restricted"}), "eu-west-1", 7),
               ExecutionTarget("wrong-region", "tenant-a", frozenset({"restricted"}), "us-east-1", 7))
    with pytest.raises(ValueError) as error:
        place(boundary, targets)
    assert "tenant_mismatch" in str(error.value) and "residency_mismatch" in str(error.value)


def test_placement_refuses_retention_that_exceeds_the_boundary():
    boundary = DataBoundary("tenant-a", "restricted", "eu-west-1", 7)
    target = ExecutionTarget(
        "too-long",
        "tenant-a",
        frozenset({"restricted"}),
        "eu-west-1",
        30,
    )
    with pytest.raises(ValueError, match="too-long:retention_too_long"):
        place(boundary, (target,))


def test_orders_investigation_cannot_run_on_wrong_residency_target():
    accepted = run_placed_orders_investigation(
        orders_data_boundary(), orders_execution_targets()
    )
    assert accepted.target_id == "orders-us-west-2"
    assert accepted.registered.journey.completed is True

    with pytest.raises(ValueError, match="residency_mismatch"):
        run_placed_orders_investigation(
            orders_data_boundary(region="eu-west-1"), orders_execution_targets()
        )
