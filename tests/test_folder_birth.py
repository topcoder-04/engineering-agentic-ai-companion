"""Enforce when reader-facing responsibility folders are born."""

from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "src" / "orders_investigation"
PACKAGE_BIRTH = {
    "domain": 1,
    "environment": 1,
    "runtime": 2,
    "decisions": 3,
    "graph": 4,
    "context": 5,
    "effects": 8,
    "memory": 10,
    "integrations": 13,
    "coordination": 17,
    "governance": 18,
    "evaluation": 22,
    "operations": 25,
    "platform": 29,
}
PLATFORM_BIRTH = {
    "identity": 29,
    "capabilities": 30,
    "authority": 31,
    "placement": 32,
    "defaults": 33,
    "releases": 34,
    "lifecycle": 35,
    "compatibility": 36,
    "risk": 37,
}


def current_chapter() -> int:
    explicit = os.getenv("COMPANION_CHAPTER")
    if explicit:
        return int(explicit)
    match = re.search(r"^#\s+Chapter\s+(\d+)\b", (ROOT / "README.md").read_text(), re.IGNORECASE | re.MULTILINE)
    return int(match.group(1)) if match else 37


def test_responsibility_packages_are_born_exactly_on_schedule():
    chapter = current_chapter()
    present = {path.name for path in SOURCE.iterdir() if path.is_dir() and not path.name.startswith("__")}
    for package, born in PACKAGE_BIRTH.items():
        assert (package in present) == (chapter >= born), (package, born, chapter)


def test_platform_subdomains_are_born_exactly_on_schedule():
    chapter = current_chapter()
    platform = SOURCE / "platform"
    present = ({path.name for path in platform.iterdir() if path.is_dir() and not path.name.startswith("__")}
               if platform.exists() else set())
    for package, born in PLATFORM_BIRTH.items():
        assert (package in present) == (chapter >= born), (package, born, chapter)


def test_graph_tasks_does_not_cross_the_chapter_three_boundary():
    assert (SOURCE / "graph" / "tasks.py").exists() == (current_chapter() >= 4)
