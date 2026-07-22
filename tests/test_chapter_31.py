from datetime import datetime, timedelta, timezone
from orders_investigation.platform.authority import CallerIdentity, Delegation, authorize


def test_delegation_is_bound_to_caller_tenant_agent_action_and_expiry():
    now = datetime(2026, 7, 21, tzinfo=timezone.utc)
    identity = CallerIdentity("user-7", "tenant-a", frozenset({"operator"}))
    grant = Delegation("d", "user-7", "tenant-a", "orders-investigator", frozenset({"report.write"}), now + timedelta(minutes=5))
    assert authorize(identity, grant, "orders-investigator", "report.write", now) == (True, ())
    assert authorize(identity, grant, "orders-investigator", "report.write", now + timedelta(minutes=6))[1] == ("delegation_expired",)
