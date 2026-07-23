from orders_investigation.evaluation.production import (
    SemanticTrace,
    TraceEvent,
)


def trace(*, kinds=("observe", "decide", "effect"), status="completed"):
    events = tuple(
        TraceEvent(
            i + 1,
            kind,
            "orders",
            f"in-{i}",
            f"out-{i}",
            ("cpu", "connections") if i == 0 else (),
            decision_reason="bounded",
            duration_ms=100,
            input_units=10,
            output_units=10,
        )
        for i, kind in enumerate(kinds)
    )
    return SemanticTrace(
        "exec-1",
        "agent-v2",
        "restricted",
        "policy-v3",
        events,
        status,
    )


def case(maximum_actions=3):
    from orders_investigation.evaluation.production import EvaluationCase

    return EvaluationCase(
        "orders-recovery",
        frozenset({"cpu", "connections"}),
        frozenset({"observe", "decide", "effect"}),
        maximum_actions,
    )


def contract(version="1"):
    from orders_investigation.platform.identity import AgentContract

    return AgentContract(
        "orders-investigator",
        version,
        "orders-oncall",
        "goal/v1",
        "trace/v2",
        ("database.read/v2",),
        "consequential/v4",
        "reasoning-restricted",
        frozenset({"restricted"}),
    )
