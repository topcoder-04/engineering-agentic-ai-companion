"""Run Chapter 2's deterministic observation perimeter."""

from orders_investigation.environment.requests import OPENING_OBSERVATION_REQUESTS
from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.boundary import ORDERS_BOUNDARY, Request


def main() -> None:
    demo = chapter_presentation(2, description=__doc__)
    demo.scenario(1, "Declared Orders observations")
    for task_id, request in sorted(OPENING_OBSERVATION_REQUESTS.items()):
        allowed = ORDERS_BOUNDARY.allows(request)
        demo.result_row(
            task_id,
            accepted=allowed,
            outcome="PERMITTED" if allowed else "REFUSED",
            detail=f"{request.source} · {request.operation}",
        )
    decisions = {
        "other environment": Request(
            "observe",
            "service_metrics",
            "payments-production",
            "payments-api",
            "latency",
        ),
        "rollback": Request(
            "rollback",
            "deployment_pipeline",
            "orders-production",
            "orders-release",
            "latest",
        ),
        "unknown operation": Request(
            "restart",
            "service_metrics",
            "orders-production",
            "orders-api",
            "latest",
        ),
    }
    demo.scenario(2, "Requests outside the declared perimeter")
    for label, request in decisions.items():
        allowed = ORDERS_BOUNDARY.allows(request)
        demo.result_row(
            label,
            accepted=allowed,
            outcome="PERMITTED" if allowed else "REFUSED BEFORE OUTSIDE WORK",
            detail=f"{request.environment} · {request.operation}",
        )
    demo.notice(
        "The flexible layer may choose among permitted observations. It cannot "
        "expand the operation, source, environment, resource, or selector."
    )


if __name__ == "__main__":
    main()
