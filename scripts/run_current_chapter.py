"""Run the demo matching the current checkpoint README."""

from __future__ import annotations

import re
import runpy
from pathlib import Path


ROOT = Path(__file__).parents[1]
match = re.search(r"Chapter\s+(\d+)", (ROOT / "README.md").read_text(), re.IGNORECASE)
if not match:
    raise SystemExit("README does not identify the current chapter")
chapter = int(match.group(1))
demo = ROOT / "examples" / f"chapter_{chapter:02d}.py"
if not demo.exists():
    raise SystemExit(f"missing current-chapter demo: {demo.relative_to(ROOT)}")
runpy.run_path(str(demo), run_name="__main__")
