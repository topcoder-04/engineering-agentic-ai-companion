"""Chapter 23: evaluate the path, not only the final answer."""
from orders_investigation.evaluation.production import EvaluationCase, SemanticTrace, TraceEvent, evaluate

trace = SemanticTrace("exec-23", "v2", "restricted", "p3", (TraceEvent(1, "forbidden_write", "orders", "in", "out", ("cpu",)),), "completed")
case = EvaluationCase("recovery", frozenset({"cpu"}), frozenset({"observe", "decide", "effect"}), 3)
result = evaluate(trace, case)
print("CHAPTER 23 — PATH EVALUATION")
print("outcome passed", result.dimensions["outcome"], "overall passed", result.passed, "reasons", result.reasons)
