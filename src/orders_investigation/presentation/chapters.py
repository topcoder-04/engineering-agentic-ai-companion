"""Chapter-local teaching contracts for the executable demos.

Each entry describes only the responsibility earned at that checkpoint.  The
registry is deliberately data-only so presentation stays separate from domain
behavior and branch projection can retain only the entries earned so far.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChapterStory:
    title: str
    question: str
    introduced: str
    problem: str
    previously_earned: str
    new_in_chapter: str
    makes_possible: str


CHAPTER_STORIES = {
    1: ChapterStory(
        "When a Good Answer Is Not the Work",
        "Can a plausible answer prove that the investigation work is complete?",
        "Observable completion conditions",
        "A persuasive answer can hide missing evidence or failed work.",
        "Nothing — this is the foundation.",
        "Answer, evidence, action, and result stay separate.",
        "Completion can depend on recorded evidence and an observed result.",
    ),
    2: ChapterStory(
        "What This Investigation May Touch",
        "Can permitted work be defined before any outside system is contacted?",
        "Observation and action perimeter",
        "A useful request can still target the wrong operation, system, or environment.",
        "Observable completion conditions",
        "Declared operations, sources, environments, resources, and selectors.",
        "Forbidden work is refused before an outside call can begin.",
    ),
    3: ChapterStory(
        "When Permitted Work Still Wastes Time",
        "Can the model choose useful work without gaining authority to execute it?",
        "Bounded model choice",
        "Several observations may be permitted while only one closes the current gap.",
        "Completion conditions · deterministic scope",
        "A model selects one declared observation; application code performs it.",
        "Flexible judgment can guide work without becoming the execution boundary.",
    ),
}
