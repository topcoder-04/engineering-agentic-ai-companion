"""Chapter 35: exceptions remain scoped, owned, controlled, and expiring."""
from datetime import datetime, timedelta, timezone
from orders_investigation.platform.lifecycle import ExceptionGrant, validate_exception

now = datetime(2026, 7, 21, tzinfo=timezone.utc); grant = ExceptionGrant("e35", "security", "residency", now + timedelta(days=1), ("manual-review",), waivable=False)
print("CHAPTER 35 — EXCEPTION LIFECYCLE")
print("decision", validate_exception(grant, "residency", now))
