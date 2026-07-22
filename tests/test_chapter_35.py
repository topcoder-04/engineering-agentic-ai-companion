from datetime import datetime, timedelta, timezone
import pytest
from orders_investigation.platform.lifecycle import (
    ExceptionGrant,
    validate_exception,
    validate_ownership,
)
from orders_investigation.runtime.journey import (
    orders_lifecycle_ownership,
    run_owned_orders_investigation,
)


def test_exception_requires_owner_control_scope_and_live_expiry():
    now = datetime(2026, 7, 21, tzinfo=timezone.utc)
    grant = ExceptionGrant("e", "security", "residency", now + timedelta(days=1), ("manual-review",), waivable=False)
    assert validate_exception(grant, "residency", now)[1] == ("boundary_not_waivable",)
    assert "exception_expired" in validate_exception(grant, "residency", now + timedelta(days=2))[1]


def test_lifecycle_ownership_requires_operator_runbook_and_rollback_owner():
    assert validate_ownership(orders_lifecycle_ownership()) == (True, ())
    missing = orders_lifecycle_ownership(owner="")
    assert validate_ownership(missing)[1] == ("lifecycle_owner_missing",)


def test_unowned_orders_candidate_cannot_execute_after_conformance():
    assert run_owned_orders_investigation(
        orders_lifecycle_ownership()
    ).registered.journey.completed is True
    with pytest.raises(
        ValueError,
        match="lifecycle_refused:lifecycle_owner_missing",
    ):
        run_owned_orders_investigation(orders_lifecycle_ownership(owner=""))
