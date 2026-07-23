import json

from orders_investigation.runtime.boundary import ORDERS_BOUNDARY
from orders_investigation.context.surface import build_decision_surface
from orders_investigation.runtime.contracts.admission import admit
from orders_investigation.decisions.model import ModelChoice
from orders_investigation.environment.scenario import current_case
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(5, description=__doc__)
    incident, graph = current_case()
    surface = build_decision_surface(incident, graph)
    choice = ModelChoice(
        "inspect_pipeline_run",
        "deploy-882 probably increased migration parallelism.",
        "a worker-count or batch-size change",
    )
    invocation = admit(choice, graph, ORDERS_BOUNDARY)
    surface_data = json.loads(surface.prompt)

    demo.scenario(1, "The model receives current bounded state")
    demo.fields(
        (
            ("Decision surface", ", ".join(sorted(surface_data))),
            ("Proposed task", choice.task_id),
            ("Model reason", choice.reason),
        ),
        style="evidence",
    )
    demo.scenario(2, "Application code resolves and admits the proposal")
    demo.decision(True, approved_label="PROPOSAL ADMITTED")
    demo.fields(
        (
            ("Task", invocation.task_id),
            ("Outside request", f"{invocation.source}/{invocation.resource}"),
            ("Reason became evidence", "NO"),
            ("Evidence gap closed", "NO — a validated result is still required"),
        )
    )
    demo.notice(
        "The model may explain why it chose the task. That explanation never "
        "becomes evidence and cannot close the pipeline-trigger gap."
    )


if __name__ == "__main__":
    main()
