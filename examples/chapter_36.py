"""Chapter 36: readers advance before writers."""
from orders_investigation.platform.compatibility import CompatibilityWindow, migration_step

window = CompatibilityWindow("trace/v1", "trace/v2", frozenset({"trace/v1", "trace/v2"}), "trace/v1")
print("CHAPTER 36 — COMPATIBLE EVOLUTION")
print("next step", migration_step(window, {"trace/v1", "trace/v2"}))
