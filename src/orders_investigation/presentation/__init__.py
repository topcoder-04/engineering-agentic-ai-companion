"""Reader-facing terminal presentation for executable chapter demos."""

import argparse

from .chapters import CHAPTER_STORIES, ChapterStory
from .terminal import (
    DemoPresentation,
    add_output_arguments,
    color_is_enabled,
    presentation_from_args,
)


def present_chapter(
    chapter: int,
    *,
    color_mode: str = "auto",
    stream=None,
) -> DemoPresentation:
    """Introduce one chapter's earned concept using an already resolved mode."""
    story = CHAPTER_STORIES[chapter]
    options = {"color_mode": color_mode}
    if stream is not None:
        options["stream"] = stream
    demo = presentation_from_args(**options)
    demo.banner(chapter, story.title, story.question)
    demo.building_block(
        introduced=story.introduced,
        problem=story.problem,
        previously_earned=story.previously_earned,
        new_in_chapter=story.new_in_chapter,
        makes_possible=story.makes_possible,
    )
    return demo


def chapter_presentation(
    chapter: int,
    *,
    description: str | None = None,
) -> DemoPresentation:
    """Parse shared output flags and introduce one chapter's earned concept."""
    parser = argparse.ArgumentParser(description=description)
    add_output_arguments(parser)
    arguments = parser.parse_args()
    return present_chapter(chapter, color_mode=arguments.color_mode)


__all__ = [
    "CHAPTER_STORIES",
    "ChapterStory",
    "DemoPresentation",
    "add_output_arguments",
    "chapter_presentation",
    "color_is_enabled",
    "present_chapter",
    "presentation_from_args",
]
