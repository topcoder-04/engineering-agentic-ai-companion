"""Chapter 31: preserve caller-bound delegated authority."""
from datetime import datetime, timedelta, timezone
from orders_investigation.platform.authority import CallerIdentity, Delegation, authorize

now = datetime(2026, 7, 21, tzinfo=timezone.utc); caller = CallerIdentity("u7", "tenant-a", frozenset({"operator"}))
grant = Delegation("d31", "u7", "tenant-a", "orders", frozenset({"report.write"}), now + timedelta(minutes=5))
print("CHAPTER 31 — DELEGATED AUTHORITY")
print("allowed", authorize(caller, grant, "orders", "report.write", now), "wrong action", authorize(caller, grant, "orders", "refund.issue", now))
