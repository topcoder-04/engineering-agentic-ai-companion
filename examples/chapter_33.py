"""Chapter 33: scaffold the safe path and expose overrides."""
from orders_investigation.platform.defaults import ScaffoldRequest, scaffold
from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.journey import run_scaffolded_orders_investigation


def main() -> None:
    demo = chapter_presentation(33, description=__doc__)
    project = scaffold(
        ScaffoldRequest("orders-investigator", "orders-oncall", "read-only")
    )
    accepted = run_scaffolded_orders_investigation()
    demo.scenario(1, "The paved path carries required controls by default")
    demo.fields(
        (
            ("Generated files", ", ".join(sorted(project.files))),
            ("Declared exceptions", project.declared_exceptions),
            ("Journey completed", accepted.registered.journey.completed),
        ),
        style="evidence",
    )
    demo.decision(True, approved_label="SCAFFOLD ADMITTED")
    demo.scenario(2, "An undeclared override becomes visible at admission")
    try:
        run_scaffolded_orders_investigation(
            overrides={"custom/router.py": "# owned"}
        )
    except ValueError as exc:
        demo.decision(False, refused_label="OVERRIDE REFUSED", reason=str(exc))
    demo.notice(
        "The scaffold makes the safe architecture easy to adopt. Escape hatches "
        "remain explicit, owned inputs rather than invisible local customization."
    )


if __name__ == "__main__":
    main()
