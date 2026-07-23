"""Build the manuscript's small reconstructable semantic trace."""

from orders_investigation.evaluation.production import (
    SemanticTrace,
    TraceEvent,
    digest,
)
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(22, description=__doc__)
    trace = SemanticTrace(
        "orders-trace-22",
        "orders-agent-v1",
        "reasoning-restricted",
        "orders-report-v1",
        (
            TraceEvent(
                1,
                "observe",
                "database-monitoring",
                digest("writer-request"),
                digest("writer-result"),
                ("writer-recovery-17",),
                duration_ms=18,
            ),
            TraceEvent(
                2,
                "decide",
                "orders-runtime",
                digest("writer-result"),
                digest("publish-proposal"),
                ("writer-recovery-17",),
                duration_ms=7,
            ),
        ),
        "completed",
    )
    integrity_reasons = trace.validate()
    demo.scenario(1, "A small trace reconstructs the meaningful path")
    demo.fields(
        (
            ("Integrity reasons", ", ".join(integrity_reasons) or "none"),
            ("Events", len(trace.events)),
            ("Path", " → ".join(event.kind for event in trace.events)),
            ("Total duration", f"{trace.total_duration_ms} ms"),
            ("Raw request present", hasattr(trace.events[0], "raw_request")),
        ),
        style="evidence",
    )
    demo.decision(not integrity_reasons, approved_label="TRACE RECONSTRUCTABLE")
    demo.notice(
        "Digests and evidence references preserve causal structure. The trace "
        "does not need raw prompts or raw dependency values to explain the path."
    )


if __name__ == "__main__":
    main()
