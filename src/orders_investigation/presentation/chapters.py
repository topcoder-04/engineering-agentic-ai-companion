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
    4: ChapterStory(
        "When Evidence Changes the Shape of the Work",
        "Can newly observed evidence reveal work that was not knowable earlier?",
        "Evidence-driven task graph",
        "A static checklist cannot represent resources discovered during investigation.",
        "Completion · scope · bounded model choice",
        "Recorded results move tasks and create only evidence-justified work.",
        "The investigation can expand without allowing the model to invent topology.",
    ),
    5: ChapterStory(
        "What the Model Sees and What May Run",
        "Can a model proposal become executable without treating its prose as evidence?",
        "Decision surface and proposal admission",
        "A model response can be stale, malformed, unsupported, or persuasive but false.",
        "Evidence-driven tasks and bounded choice",
        "Current context, typed proposals, readiness checks, and deterministic admission.",
        "Only a current declared task crosses from judgment into runtime execution.",
    ),
    6: ChapterStory(
        "When Judgment Becomes a Dependency",
        "Can model unavailability consume a bounded, observable amount of the run?",
        "Decision budget and attempt ledger",
        "Retries can silently exhaust time, cost, and the investigation deadline.",
        "Typed proposal admission",
        "Call, retry, elapsed-time, and usage limits with recorded stop reasons.",
        "The run can fail closed when judgment is unavailable or exhausted.",
    ),
    7: ChapterStory(
        "Keeping Changed Work Alive After a Restart",
        "Can the investigation resume without reconstructing state from memory?",
        "Durable workflow state",
        "A process restart can erase evidence, ready work, and consumed decision budget.",
        "Bounded decisions · evidence-driven graph",
        "The incident, graph, hypothesis history, and attempt ledger persist together.",
        "Recovery resumes from recorded state instead of replaying uncertain work.",
    ),
    8: ChapterStory(
        "Trying Again Without Doing It Twice",
        "Can a lost response be retried without applying the report update twice?",
        "Idempotent effect application",
        "The caller may not know whether an effect committed before its response was lost.",
        "Durable workflow state",
        "Immutable intent, stable idempotency key, and atomic effect deduplication.",
        "The same logical effect can be retried safely after transport uncertainty.",
    ),
}
