"""Small, dependency-free terminal presentation helpers for chapter demos.

Color is enabled automatically only for an interactive terminal. ``--color``
and ``--plain`` let a reader choose explicitly, while ``NO_COLOR`` keeps the
standard opt-out available to shell users and automation.
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import TextIO


RESET = "\033[0m"
STYLES = {
    "title": "\033[1;36m",
    "concept": "\033[1;36m",
    "context": "\033[2m",
    "evidence": "\033[33m",
    "approved": "\033[1;32m",
    "refused": "\033[1;31m",
    "path": "\033[35m",
    "heading": "\033[1m",
}

MOVEMENT_STYLES = {
    1: "\033[1;38;2;85;217;255m",
    2: "\033[1;38;2;99;229;154m",
    3: "\033[1;38;2;255;209;102m",
    4: "\033[1;38;2;255;130;170m",
    5: "\033[1;38;2;185;154;255m",
}


def add_output_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the presentation options shared by every demo entry point."""
    output = parser.add_mutually_exclusive_group()
    output.add_argument(
        "--color",
        action="store_const",
        const="always",
        dest="color_mode",
        help="show ANSI color even when output is not attached to a terminal",
    )
    output.add_argument(
        "--plain",
        action="store_const",
        const="never",
        dest="color_mode",
        help="disable ANSI color",
    )
    parser.set_defaults(color_mode="auto")


def color_is_enabled(
    stream: TextIO,
    mode: str = "auto",
    *,
    environment: Mapping[str, str] | None = None,
) -> bool:
    """Resolve explicit flags, ``NO_COLOR``, and terminal capability."""
    if mode == "always":
        return True
    if mode == "never":
        return False
    env = os.environ if environment is None else environment
    return "NO_COLOR" not in env and stream.isatty()


@dataclass
class DemoPresentation:
    """Render one chapter's behavioral proof in a consistent visual language."""

    stream: TextIO = sys.stdout
    color_mode: str = "auto"

    def __post_init__(self) -> None:
        self._color = color_is_enabled(self.stream, self.color_mode)

    def _styled(self, text: str, style: str) -> str:
        if not self._color:
            return text
        return f"{STYLES[style]}{text}{RESET}"

    def _styled_with_code(self, text: str, code: str) -> str:
        if not self._color:
            return text
        return f"{code}{text}{RESET}"

    def line(self, text: str = "", *, style: str | None = None) -> None:
        print(self._styled(text, style) if style else text, file=self.stream)

    def banner(self, chapter: int, title: str, question: str) -> None:
        label = f"CHAPTER {chapter} · {title.upper()}"
        rule = "━" * min(76, max(48, len(label)))
        movement = min(5, ((chapter - 1) // 7) + 1)
        style = MOVEMENT_STYLES[movement]
        print(self._styled_with_code(rule, style), file=self.stream)
        print(self._styled_with_code(label, style), file=self.stream)
        print(self._styled_with_code(rule, style), file=self.stream)
        self.line(question, style="context")

    def section(self, title: str) -> None:
        self.line()
        self.line(title.upper(), style="heading")

    def building_block(
        self,
        *,
        introduced: str,
        problem: str,
        previously_earned: str,
        new_in_chapter: str,
        makes_possible: str,
    ) -> None:
        self.section("Building block introduced")
        self.line(f"  {introduced}", style="concept")
        self._field("Problem it solves", problem)
        self._field("Previously earned", previously_earned, style="context")
        self._field("New in this chapter", new_in_chapter, style="concept")
        self._field("What becomes possible", makes_possible)

    def scenario(self, number: int, title: str) -> None:
        self.section(f"Scenario {number} · {title}")

    def fields(
        self,
        values: Mapping[str, object] | Iterable[tuple[str, object]],
        *,
        style: str | None = None,
    ) -> None:
        items = values.items() if isinstance(values, Mapping) else values
        for label, value in items:
            self._field(label, str(value), style=style)

    def _field(self, label: str, value: str, *, style: str | None = None) -> None:
        prefix = f"  {label:<34}"
        continuation = " " * len(prefix)
        lines = textwrap.wrap(
            value,
            width=66,
            break_long_words=False,
            break_on_hyphens=False,
        ) or [""]
        for index, line in enumerate(lines):
            rendered_value = self._styled(line, style) if style else line
            indentation = prefix if index == 0 else continuation
            print(f"{indentation}{rendered_value}", file=self.stream)

    def state(self, label: str, complete: bool, detail: str = "") -> None:
        if complete:
            value = "✓ COMPLETE"
            style = "approved"
        else:
            value = "✗ INCOMPLETE"
            style = "refused"
        if detail:
            value = f"{value} · {detail}"
        self._field(label, value, style=style)

    def decision(
        self,
        approved: bool,
        *,
        approved_label: str = "APPROVED",
        refused_label: str = "REFUSED",
        reason: str = "",
    ) -> None:
        if approved:
            value = f"✓ {approved_label}"
            style = "approved"
        else:
            value = f"✗ {refused_label}"
            style = "refused"
        self._field("Decision", value, style=style)
        if reason:
            self._field("Reason", reason, style="evidence")

    def execution(self, executed: bool, detail: str) -> None:
        if executed:
            value = f"✓ {detail}"
            style = "approved"
        else:
            value = f"✗ NOT EXECUTED · {detail}"
            style = "refused"
        self._field("Execution", value, style=style)

    def path(self, steps: Sequence[str]) -> None:
        self._field("Path", " → ".join(steps), style="path")

    def result_row(
        self,
        label: str,
        *,
        accepted: bool,
        outcome: str,
        detail: str = "",
    ) -> None:
        marker = "✓" if accepted else "✗"
        status = f"{marker} {outcome}"
        if detail:
            status = f"{status} · {detail}"
        self._field(label, status, style="approved" if accepted else "refused")

    def numbered_map(self, rows: Iterable[tuple[str, str]]) -> None:
        for index, (label, detail) in enumerate(rows, start=1):
            self._field(f"{index}. {label}", detail)

    def notice(self, text: str) -> None:
        self.section("What to notice")
        for line in textwrap.wrap(
            text,
            width=96,
            break_long_words=False,
            break_on_hyphens=False,
        ):
            self.line(f"  {line}", style="concept")


def presentation_from_args(
    color_mode: str,
    *,
    stream: TextIO = sys.stdout,
) -> DemoPresentation:
    return DemoPresentation(stream=stream, color_mode=color_mode)
