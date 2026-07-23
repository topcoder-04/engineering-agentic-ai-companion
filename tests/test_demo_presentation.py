import io
import re
import subprocess
import sys

from orders_investigation.presentation import CHAPTER_STORIES, color_is_enabled


ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def run_demo(*arguments: str) -> str:
    completed = subprocess.run(
        [sys.executable, *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def test_chapter_01_demo_teaches_observable_completion_in_plain_text():
    output = run_demo(
        "-m",
        "orders_investigation.demo",
        "chapter-01",
        "--plain",
    )

    assert "BUILDING BLOCK INTRODUCED" in output
    assert "Observable completion conditions" in output
    assert "SCENARIO 2 · THE REPORT UPDATE SUCCEEDS" in output
    assert "accepted" in output
    assert "✗ INCOMPLETE" in output
    assert "successful action changes one observed fact" in output
    assert not ANSI_ESCAPE.search(output)


def test_every_earned_chapter_teaches_its_building_block_and_behavior():
    for chapter, story in CHAPTER_STORIES.items():
        output = run_demo(f"examples/chapter_{chapter:02d}.py", "--plain")

        assert f"CHAPTER {chapter} · {story.title.upper()}" in output
        assert "BUILDING BLOCK INTRODUCED" in output
        assert story.introduced in output
        assert "SCENARIO 1 ·" in output
        assert "WHAT TO NOTICE" in output
        assert not ANSI_ESCAPE.search(output)


def test_forced_color_changes_style_without_changing_semantics():
    plain = run_demo("examples/chapter_01.py", "--plain")
    colored = run_demo("examples/chapter_01.py", "--color")

    assert "\033[" in colored
    assert ANSI_ESCAPE.sub("", colored) == plain


def test_each_movement_uses_its_own_banner_color():
    movement_colors = (
        "\033[1;38;2;85;217;255m",
        "\033[1;38;2;99;229;154m",
        "\033[1;38;2;255;209;102m",
        "\033[1;38;2;255;130;170m",
        "\033[1;38;2;185;154;255m",
    )
    for chapter in CHAPTER_STORIES:
        movement = min(5, ((chapter - 1) // 7) + 1)
        output = run_demo(f"examples/chapter_{chapter:02d}.py", "--color")
        assert movement_colors[movement - 1] in output


def test_no_color_disables_automatic_color_on_an_interactive_stream():
    class InteractiveStream(io.StringIO):
        def isatty(self) -> bool:
            return True

    assert color_is_enabled(InteractiveStream(), environment={})
    assert not color_is_enabled(
        InteractiveStream(),
        environment={"NO_COLOR": ""},
    )


def test_current_chapter_runner_passes_the_plain_flag_through():
    chapter = max(CHAPTER_STORIES)
    story = CHAPTER_STORIES[chapter]
    output = run_demo(
        "scripts/run_current_chapter.py",
        f"chapter-{chapter:02d}",
        "--plain",
    )

    assert f"CHAPTER {chapter} · {story.title.upper()}" in output
    assert not ANSI_ESCAPE.search(output)
