"""Chapter 36: compatible contract evolution."""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CompatibilityWindow:
    old_version: str
    new_version: str
    readers_accept: frozenset[str]
    writers_emit: str


def migration_step(window: CompatibilityWindow, observed_readers: Iterable[str]) -> str:
    readers = set(observed_readers)
    if not readers <= window.readers_accept:
        return "hold_incompatible_reader"
    if window.writers_emit == window.old_version:
        return "advance_readers_first"
    if window.writers_emit == window.new_version and window.old_version in readers:
        return "continue_dual_read"
    return "retire_old_version"
