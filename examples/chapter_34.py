"""Chapter 34: bind release evidence to the exact artifact."""
from orders_investigation.platform.releases import ConformanceReceipt, release_conforms
from orders_investigation.platform.identity import AgentContract

contract = AgentContract("orders", "1", "orders-oncall", "goal/v1", "trace/v2", ("db.read/v2",), "policy/v3", "restricted", frozenset({"restricted"}))
receipt = ConformanceReceipt("candidate-a", contract.manifest_digest, "suite-5", frozenset({"trace", "policy"}), frozenset())
print("CHAPTER 34 — CONFORMANCE RECEIPT")
print("candidate-a", release_conforms("candidate-a", contract, receipt, {"trace", "policy"}), "candidate-b", release_conforms("candidate-b", contract, receipt, {"trace", "policy"}))
