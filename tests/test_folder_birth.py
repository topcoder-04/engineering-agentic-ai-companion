"""Enforce the reader-facing architecture and its chapter birth schedule."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "src" / "orders_investigation"
PACKAGE_BIRTH = {
    "domain": 1, "environment": 1, "presentation": 1,
    "runtime": 2, "decisions": 3,
    "graph": 4, "context": 5, "effects": 8, "memory": 10,
    "integrations": 13, "coordination": 17, "governance": 18,
    "evaluation": 22, "operations": 25, "platform": 29,
}
PLATFORM_BIRTH = {
    "identity": 29, "capabilities": 30, "authority": 31,
    "placement": 32, "defaults": 33, "releases": 34,
    "lifecycle": 35, "compatibility": 36, "risk": 37,
}


def current_chapter() -> int:
    explicit = os.getenv("COMPANION_CHAPTER")
    if explicit:
        return int(explicit)
    match = re.search(
        r"^#\s+Chapter\s+(\d+)\b",
        (ROOT / "README.md").read_text(),
        re.IGNORECASE | re.MULTILINE,
    )
    return int(match.group(1)) if match else 37


def test_responsibility_packages_are_born_exactly_on_schedule():
    chapter = current_chapter()
    present = {
        path.parent.name
        for path in SOURCE.glob("*/__init__.py")
    }
    for package, born in PACKAGE_BIRTH.items():
        assert (package in present) == (chapter >= born), (package, born, chapter)


def test_platform_subdomains_are_born_exactly_on_schedule():
    chapter = current_chapter()
    platform = SOURCE / "platform"
    present = (
        {
            path.parent.name
            for path in platform.glob("*/__init__.py")
        }
        if platform.exists()
        else set()
    )
    for package, born in PLATFORM_BIRTH.items():
        assert (package in present) == (chapter >= born), (package, born, chapter)


def test_graph_tasks_does_not_cross_the_chapter_three_boundary():
    assert (SOURCE / "graph" / "tasks.py").exists() == (current_chapter() >= 4)


def test_generic_code_buckets_and_obsolete_flat_modules_are_forbidden():
    forbidden = {"utils", "helpers", "misc"}
    assert not [
        path for path in SOURCE.rglob("*")
        if path.is_dir() and path.name in forbidden
    ]
    allowed_root = {"__init__.py", "demo.py", "live_demo.py"}
    assert {path.name for path in SOURCE.glob("*.py")} <= allowed_root


def test_readme_commands_and_code_map_are_executable():
    readme = (ROOT / "README.md").read_text()
    chapter = current_chapter()
    assert "python3 -m venv .venv" in readme
    assert "python -m pip install -e '.[test]'" in readme
    assert f"python -m pytest tests/test_chapter_{chapter:02d}.py" in readme
    assert "python -m pytest" in readme
    assert "python scripts/run_current_chapter.py" in readme
    assert (
        f"python -m orders_investigation.demo chapter-{chapter:02d}"
        in readme
    )
    assert "`uv` is optional" in readme
    assert "uv sync --extra test" in readme
    assert "uv run --no-sync pytest" in readme
    assert "uv run --no-sync python scripts/run_current_chapter.py" in readme
    assert "building block introduced" in readme.lower()
    assert "--plain" in readme
    assert "--color" in readme
    assert "NO_COLOR" in readme
    assert "NOT EXECUTED" in readme
    assert "tests/test_chapter_*.py" not in readme
    assert "`platform.py`" not in readme
    assert "CI runs the same commands" not in readme
    assert "scripts/run_current_chapter.py" in readme
    for shared_path in (
        "src/orders_investigation/presentation/__init__.py",
        "src/orders_investigation/presentation/chapters.py",
        "src/orders_investigation/presentation/terminal.py",
        "tests/test_demo_presentation.py",
    ):
        assert shared_path in readme
    mapped = [
        line.strip() for line in readme.splitlines()
        if line.strip().startswith("src/orders_investigation/")
    ]
    assert mapped
    assert all((ROOT / path).exists() for path in mapped)


def test_architecture_describes_only_the_current_checkpoint():
    chapter = current_chapter()
    architecture = (ROOT / "ARCHITECTURE.md").read_text()
    assert f"Current checkpoint: Chapter {chapter}" in architecture
    documented = {
        int(match.group(1))
        for match in re.finditer(r"^\|\s*(\d+)\s*\|", architecture, re.MULTILINE)
    }
    assert documented == set(range(1, chapter + 1))
    if chapter == 37:
        assert "complete architecture earned across all 37 chapters" in architecture
        assert "Later responsibilities are intentionally absent" not in architecture


def test_book_and_readme_entrypoints_execute_the_same_checkpoint():
    chapter = current_chapter()
    book = subprocess.run(
        [
            sys.executable,
            "-m",
            "orders_investigation.demo",
            f"chapter-{chapter:02d}",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    runner = subprocess.run(
        [sys.executable, "scripts/run_current_chapter.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert book.returncode == 0, book.stderr
    assert runner.returncode == 0, runner.stderr
    assert book.stdout == runner.stdout


def test_interlude_replays_exist_at_their_birth_checkpoints():
    chapter = current_chapter()
    cases = []
    if chapter >= 7:
        cases.append("foundation-replay")
    if chapter >= 14:
        cases.append("part-2-replay")
    for command in cases:
        result = subprocess.run(
            [sys.executable, "-m", "orders_investigation.demo", command],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
