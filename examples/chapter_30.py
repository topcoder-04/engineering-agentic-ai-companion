"""Chapter 30: admit only compatible capabilities."""
from orders_investigation.platform.capabilities import CapabilityProfile
from orders_investigation.platform.identity import AgentRegistry
from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.journey import (
    orders_agent_contract,
    orders_capability_profile,
    run_capability_admitted_orders_investigation,
)


def main() -> None:
    demo = chapter_presentation(30, description=__doc__)
    registry = AgentRegistry()
    registry.register(orders_agent_contract())
    accepted = run_capability_admitted_orders_investigation(
        registry, orders_capability_profile()
    )
    demo.scenario(1, "The supplied profile satisfies the registered contract")
    demo.fields(
        (
            ("Profile", orders_capability_profile().capability_id),
            ("Journey completed", accepted.journey.completed),
        ),
        style="evidence",
    )
    demo.decision(True, approved_label="CAPABILITIES ADMITTED")
    demo.scenario(2, "A copied but incompatible profile is refused")
    try:
        run_capability_admitted_orders_investigation(
            registry,
            CapabilityProfile(
                "read-only",
                frozenset(),
                frozenset(),
                frozenset(),
                frozenset(),
            ),
        )
    except ValueError as exc:
        demo.decision(False, refused_label="CAPABILITIES REFUSED", reason=str(exc))
    demo.notice(
        "Admission compares required model, tool, policy, and data capabilities. "
        "A familiar profile name cannot compensate for missing capability proof."
    )


if __name__ == "__main__":
    main()
