import pytest
from orders_investigation.platform.placement import DataBoundary, ExecutionTarget, place


def test_placement_refuses_every_least_wrong_target():
    boundary = DataBoundary("tenant-a", "restricted", "eu-west-1", 7)
    targets = (ExecutionTarget("wrong-tenant", "tenant-b", frozenset({"restricted"}), "eu-west-1", 7),
               ExecutionTarget("wrong-region", "tenant-a", frozenset({"restricted"}), "us-east-1", 7))
    with pytest.raises(ValueError) as error:
        place(boundary, targets)
    assert "tenant_mismatch" in str(error.value) and "residency_mismatch" in str(error.value)
