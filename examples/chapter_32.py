"""Chapter 32: placement must satisfy every data boundary."""
from orders_investigation.platform.placement import DataBoundary, ExecutionTarget, place

boundary = DataBoundary("tenant-a", "restricted", "eu-west-1", 7)
targets = (ExecutionTarget("wrong", "tenant-a", frozenset({"restricted"}), "us-east-1", 7), ExecutionTarget("exact", "tenant-a", frozenset({"restricted"}), "eu-west-1", 7))
print("CHAPTER 32 — DATA PLACEMENT")
print("selected target", place(boundary, targets))
