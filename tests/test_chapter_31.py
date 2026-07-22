from datetime import datetime, timedelta, timezone
from orders_investigation.platform.authority import CallerIdentity, Delegation, authorize
import pytest
from orders_investigation.runtime.journey import (
    orders_caller,
    orders_delegation,
    run_delegated_orders_investigation,
)


def test_delegation_is_bound_to_caller_tenant_agent_action_and_expiry():
    now = datetime(2026, 7, 21, tzinfo=timezone.utc)
    identity = CallerIdentity("user-7", "tenant-a", frozenset({"operator"}))
    grant = Delegation("d", "user-7", "tenant-a", "orders-investigator", frozenset({"report.write"}), now + timedelta(minutes=5))
    assert authorize(identity, grant, "orders-investigator", "report.write", now) == (True, ())
    assert authorize(identity, grant, "orders-investigator", "report.write", now + timedelta(minutes=6))[1] == ("delegation_expired",)


def test_every_delegation_mismatch_remains_visible():
    now = datetime(2026, 7, 21, tzinfo=timezone.utc)
    identity = CallerIdentity("user-8", "tenant-b", frozenset({"operator"}))
    grant = Delegation(
        "d",
        "user-7",
        "tenant-a",
        "orders-investigator",
        frozenset({"report.write"}),
        now - timedelta(seconds=1),
    )
    assert authorize(identity, grant, "search-investigator", "refund.issue", now) == (
        False,
        (
            "delegated_subject_mismatch",
            "delegated_tenant_mismatch",
            "delegated_agent_mismatch",
            "action_not_delegated",
            "delegation_expired",
        ),
    )


def test_orders_report_write_cannot_run_under_undelegated_caller_action():
    assert run_delegated_orders_investigation(
        orders_caller(), orders_delegation()
    ).journey.completed is True

    with pytest.raises(
        ValueError,
        match="caller_authority_refused:action_not_delegated",
    ):
        run_delegated_orders_investigation(
            orders_caller(), orders_delegation(), action="refund.issue"
        )
