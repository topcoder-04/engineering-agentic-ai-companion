from datetime import datetime, timedelta, timezone
from orders_investigation.platform.lifecycle import ExceptionGrant, validate_exception


def test_exception_requires_owner_control_scope_and_live_expiry():
    now = datetime(2026, 7, 21, tzinfo=timezone.utc)
    grant = ExceptionGrant("e", "security", "residency", now + timedelta(days=1), ("manual-review",), waivable=False)
    assert validate_exception(grant, "residency", now)[1] == ("boundary_not_waivable",)
    assert "exception_expired" in validate_exception(grant, "residency", now + timedelta(days=2))[1]
