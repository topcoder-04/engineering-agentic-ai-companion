"""Chapter 33: scaffold the safe path and expose overrides."""
from orders_investigation.platform.defaults import ScaffoldRequest, scaffold

result = scaffold(ScaffoldRequest("orders", "orders-oncall", "read-only"), {"custom/router.py": "# owned"})
print("CHAPTER 33 — SAFE DEFAULTS")
print("files", sorted(result.files), "declared exceptions", result.declared_exceptions)
