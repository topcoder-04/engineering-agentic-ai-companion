"""Run the demo matching the current checkpoint README.

An explicit ``chapter-NN`` argument is accepted for automation. With no
argument, the current checkpoint is discovered from the branch-local README.
"""

from __future__ import annotations

import argparse
import re
import runpy
import sys
from pathlib import Path

from orders_investigation.presentation import add_output_arguments


ROOT = Path(__file__).parents[1]


def current_chapter(argument: str | None = None) -> int:
    if argument is not None:
        match = re.fullmatch(r"chapter-(\d{2})", argument)
        if not match:
            raise SystemExit("expected chapter-NN")
        return int(match.group(1))

    readme = (ROOT / "README.md").read_text()
    heading = re.search(
        r"^#\s+Chapter\s+(\d+)\b",
        readme,
        re.IGNORECASE | re.MULTILINE,
    )
    if heading:
        return int(heading.group(1))
    complete = re.search(r"complete Chapter\s+(\d+)\s+journey", readme, re.IGNORECASE)
    if complete:
        return int(complete.group(1))
    raise SystemExit("README does not identify the current chapter")


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("checkpoint", nargs="?", help="explicit chapter-NN checkpoint")
add_output_arguments(parser)
arguments = parser.parse_args()

chapter = current_chapter(arguments.checkpoint)
demo = ROOT / "examples" / f"chapter_{chapter:02d}.py"
if not demo.exists():
    raise SystemExit(f"missing current-chapter demo: {demo.relative_to(ROOT)}")
output_flag = {
    "always": "--color",
    "never": "--plain",
}.get(arguments.color_mode)
sys.argv = [str(demo), *([output_flag] if output_flag else [])]
runpy.run_path(str(demo), run_name="__main__")
