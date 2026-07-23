"""Chapter 28: route only to an exact healthy fleet cell."""
from orders_investigation.operations.fleet import (
    Cell,
    FleetRequest,
    route_released_candidate,
)
from orders_investigation.runtime.journey import gate_orders_release, run_orders_investigation
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(28, description=__doc__)
    cells = (
        Cell("full", "us", "orders-agent-v1", "orders-report-v1", 1, 1, True, "canary"),
        Cell("ready", "us", "orders-agent-v1", "orders-report-v1", 4, 1, True, "canary"),
    )
    request = FleetRequest("r-28", "us", "orders-agent-v1", "orders-report-v1", "canary")
    accepted = run_orders_investigation()
    refused = run_orders_investigation(evidence_current=False)
    admitted = route_released_candidate(
        cells, request, gate_orders_release((accepted,))
    )
    blocked = route_released_candidate(
        cells, request, gate_orders_release((accepted, refused))
    )
    demo.scenario(1, "A released candidate finds an exact healthy cell")
    demo.fields(
        (
            ("Selected cell", admitted.cell_id),
            ("Region", request.region),
            ("Rollout ring", request.rollout_stage),
        ),
        style="evidence",
    )
    demo.decision(admitted.cell_id is not None, approved_label="FLEET ROUTE ADMITTED")
    demo.scenario(2, "A failed release cannot enter an otherwise healthy fleet")
    demo.fields((("Reasons", ", ".join(blocked.reasons)),), style="evidence")
    demo.execution(
        blocked.cell_id is not None,
        "release gate blocked fleet routing",
    )
    demo.notice(
        "Fleet health and capacity cannot override a failed behavioral release. "
        "Both the candidate and the exact cell must be eligible."
    )


if __name__ == "__main__":
    main()
