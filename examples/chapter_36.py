"""Chapter 36: readers advance before writers."""
from orders_investigation.platform.compatibility import migration_step
from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.journey import (
    orders_compatibility_window,
    run_compatible_orders_investigation,
)


def main() -> None:
    demo = chapter_presentation(36, description=__doc__)
    window = orders_compatibility_window()
    accepted = run_compatible_orders_investigation(
        window, frozenset({"trace/v2"})
    )
    demo.scenario(1, "Compatible readers advance before the writer")
    demo.fields(
        (
            ("Next migration step", migration_step(window, {"trace/v1", "trace/v2"})),
            ("Candidate readers", "trace/v2"),
            ("Journey completed", accepted.registered.journey.completed),
        ),
        style="evidence",
    )
    demo.decision(True, approved_label="COMPATIBILITY PROVEN")
    demo.scenario(2, "An unsupported reader holds the candidate")
    try:
        run_compatible_orders_investigation(
            orders_compatibility_window(), frozenset({"trace/v0"})
        )
    except ValueError as exc:
        demo.decision(False, refused_label="COMPATIBILITY REFUSED", reason=str(exc))
    demo.notice(
        "The window makes overlap explicit: readers learn the new form before "
        "writers depend on it. An unknown reader prevents the migration step."
    )


if __name__ == "__main__":
    main()
