import argparse
import re
import runpy
import sys
from pathlib import Path

from orders_investigation.domain.investigation import ReportUpdateResult
from orders_investigation.environment.opening_case import build_opening_case
from orders_investigation.presentation import (
    add_output_arguments,
    present_chapter,
)


def _run_repository_example(
    name: str,
    filename: str,
    *,
    color_mode: str,
) -> None:
    root = Path(__file__).resolve().parents[2]
    example = root / "examples" / filename
    if not example.exists():
        raise SystemExit(f"This checkpoint does not yet support {name!r}.")
    output_flag = {
        "always": "--color",
        "never": "--plain",
    }.get(color_mode)
    sys.argv = [str(example), *([output_flag] if output_flag else [])]
    runpy.run_path(str(example), run_name="__main__")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a companion chapter demo.")
    parser.add_argument("command", nargs="?", default="chapter-01")
    add_output_arguments(parser)
    arguments = parser.parse_args()
    command = arguments.command
    if command == "foundation-replay":
        _run_repository_example(
            command,
            "foundation_replay.py",
            color_mode=arguments.color_mode,
        )
        return
    if command == "part-2-replay":
        _run_repository_example(
            command,
            "part_2_replay.py",
            color_mode=arguments.color_mode,
        )
        return
    match = re.fullmatch(r"chapter-(\d{2})", command)
    if not match:
        raise SystemExit(
            "expected chapter-NN, foundation-replay, or part-2-replay"
        )
    chapter = int(match.group(1))
    if chapter > 1:
        _run_repository_example(
            command,
            f"chapter_{chapter:02d}.py",
            color_mode=arguments.color_mode,
        )
        return

    demo = present_chapter(1, color_mode=arguments.color_mode)
    investigation = build_opening_case()
    demo.scenario(1, "The opening case")
    demo.fields(
        (
            ("Current hypothesis", investigation.current_hypothesis),
            (
                "Recorded evidence",
                ", ".join(sorted(key.value for key in investigation.evidence)),
            ),
            (
                "Missing evidence",
                ", ".join(
                    sorted(key.value for key in investigation.missing_evidence)
                ),
            ),
            ("Report update", investigation.report_update_result.value),
        )
    )
    demo.state(
        "Investigation",
        investigation.investigation_complete,
        "evidence and report result are both required",
    )

    investigation.report_update_result = ReportUpdateResult.ACCEPTED
    demo.scenario(2, "The report update succeeds")
    demo.fields(
        (
            ("Report update", investigation.report_update_result.value),
            (
                "Missing evidence",
                ", ".join(
                    sorted(key.value for key in investigation.missing_evidence)
                ),
            ),
        )
    )
    demo.state(
        "Investigation",
        investigation.investigation_complete,
        "the visible artifact exists, but required evidence is incomplete",
    )
    demo.notice(
        "A successful action changes one observed fact. It cannot erase "
        "unfinished evidence work."
    )


if __name__ == "__main__":
    main()
