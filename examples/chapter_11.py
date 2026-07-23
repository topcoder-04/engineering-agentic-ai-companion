from orders_investigation.environment.scenario import current_case
from orders_investigation.graph.spine import SpineTransitionRefused, orders_spine
from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.boundary import ORDERS_BOUNDARY


def main() -> None:
    demo = chapter_presentation(11, description=__doc__)
    spine = orders_spine()
    spine.advance("writer_activity")
    spine.advance("migration_job")
    _, graph = current_case()
    request = graph.tasks["inspect_replication_delay"].request
    ready = "inspect_replication_delay" in graph.ready_ids()
    permitted = ORDERS_BOUNDARY.allows(request)

    demo.scenario(1, "Ready and permitted work is outside the current milestone")
    demo.fields(
        (
            ("Current question", spine.current.question),
            ("Allowed tasks", ", ".join(spine.current.allowed_tasks)),
            ("Boundary permits task", permitted),
            ("Graph marks task ready", ready),
        ),
        style="evidence",
    )
    try:
        spine.admit_task("inspect_replication_delay")
    except SpineTransitionRefused as error:
        demo.decision(False, refused_label="TASK SPINE REFUSED DRIFT", reason=str(error))
    demo.notice(
        "Scope and readiness are necessary but not sufficient. The persistent "
        "spine keeps permitted work aligned with the current milestone."
    )


if __name__ == "__main__":
    main()
