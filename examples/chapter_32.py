"""Chapter 32: placement must satisfy every data boundary."""
from orders_investigation.runtime.journey import (
    orders_data_boundary,
    orders_execution_targets,
    run_placed_orders_investigation,
)
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(32, description=__doc__)
    boundary = orders_data_boundary()
    accepted = run_placed_orders_investigation(
        boundary, orders_execution_targets()
    )
    demo.scenario(1, "One target satisfies every data obligation")
    demo.fields(
        (
            ("Tenant", boundary.tenant_id),
            ("Residency", boundary.region),
            ("Selected target", accepted.target_id),
            ("Journey completed", accepted.registered.journey.completed),
        ),
        style="evidence",
    )
    demo.decision(True, approved_label="PLACEMENT PROVEN")
    demo.scenario(2, "Wrong residency prevents all investigation work")
    try:
        run_placed_orders_investigation(
            orders_data_boundary(region="us-east-1"), orders_execution_targets()
        )
    except ValueError as exc:
        demo.decision(False, refused_label="PLACEMENT REFUSED", reason=str(exc))
    demo.notice(
        "Authorization does not imply placement. Tenant, data class, residency, "
        "and retention must all match one exact execution target."
    )


if __name__ == "__main__":
    main()
