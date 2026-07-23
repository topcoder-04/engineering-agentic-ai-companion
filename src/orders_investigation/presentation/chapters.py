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
}
