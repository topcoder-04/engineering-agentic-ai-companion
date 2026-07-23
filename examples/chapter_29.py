"""Chapter 29: register an immutable agent identity."""
from orders_investigation.platform.identity import AgentRegistry
from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.journey import (
    orders_agent_contract,
    run_registered_orders_investigation,
)


def main() -> None:
    demo = chapter_presentation(29, description=__doc__)
    registry = AgentRegistry()
    digest = registry.register(orders_agent_contract())
    accepted = run_registered_orders_investigation(registry)
    demo.scenario(1, "The exact registered workload starts the journey")
    demo.fields(
        (
            ("Agent", accepted.contract.agent_id),
            ("Version", accepted.contract.version),
            ("Owner", accepted.contract.owner),
            ("Manifest digest", digest[:12] + "…"),
        ),
        style="evidence",
    )
    demo.execution(accepted.journey.completed, "registered Orders journey completed")
    demo.scenario(2, "An unregistered version cannot start")
    try:
        run_registered_orders_investigation(registry, version="2")
    except ValueError as exc:
        demo.decision(False, refused_label="IDENTITY REFUSED", reason=str(exc))
    demo.notice(
        "A mutable display name is not launch identity. The exact versioned "
        "contract and its digest must resolve before any investigation work begins."
    )


if __name__ == "__main__":
    main()
