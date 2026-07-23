"""Project useful operational fields without raw content."""

from orders_investigation.evaluation.production import (
    SemanticTrace,
    TraceEvent,
    digest,
)
from orders_investigation.operations.observability import operational_view
from orders_investigation.presentation import chapter_presentation


trace = SemanticTrace(
    "orders-observation-25",
    "orders-agent-v1",
    "reasoning",
    "orders-report-v1",
    (
        TraceEvent(
            1,
            "observe",
            "database-monitoring",
            digest("request"),
            digest("result"),
            ("writer-recovery-17", "orders-recovery-17"),
            duration_ms=18,
            input_units=12,
            output_units=8,
        ),
    ),
    "completed",
)
def main() -> None:
    demo = chapter_presentation(25, description=__doc__)
    event = operational_view(trace)[0]
    demo.scenario(1, "Operators receive a useful redacted projection")
    demo.fields(
        (
            ("Component", event.component),
            ("Event kind", event.kind),
            ("Evidence references", event.evidence_count),
            ("Model units", event.units),
            ("Raw evidence exposed", hasattr(event, "raw_evidence")),
        ),
        style="evidence",
    )
    demo.decision(True, approved_label="OPERATIONAL VIEW ADMITTED")
    demo.notice(
        "Counts, timing, units, digests, and outcomes remain observable. Raw "
        "evidence and prompts remain outside the production operations surface."
    )


if __name__ == "__main__":
    main()
