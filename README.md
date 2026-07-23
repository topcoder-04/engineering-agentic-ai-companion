# Chapter 2 — What This Investigation May Touch

This cumulative checkpoint implements only the boundary earned by Chapter 2; all earlier behavior remains executable.

## What changes here

- `ARCHITECTURE.md`
- `src/orders_investigation/__init__.py`
- `src/orders_investigation/demo.py`
- `src/orders_investigation/domain/__init__.py`
- `src/orders_investigation/domain/evidence.py`
- `src/orders_investigation/domain/investigation.py`
- `src/orders_investigation/environment/__init__.py`
- `src/orders_investigation/environment/opening_case.py`
- `src/orders_investigation/environment/requests.py`
- `src/orders_investigation/runtime/__init__.py`
- `src/orders_investigation/runtime/boundary.py`
- `tests/test_chapter_01.py`
- `tests/test_chapter_02.py`

## Code map

```text
src/orders_investigation/__init__.py
src/orders_investigation/demo.py
src/orders_investigation/domain/__init__.py
src/orders_investigation/domain/evidence.py
src/orders_investigation/domain/investigation.py
src/orders_investigation/environment/__init__.py
src/orders_investigation/environment/opening_case.py
src/orders_investigation/environment/requests.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
examples/chapter_02.py
tests/test_chapter_02.py
scripts/run_current_chapter.py
src/orders_investigation/presentation/__init__.py
src/orders_investigation/presentation/chapters.py
src/orders_investigation/presentation/terminal.py
tests/test_demo_presentation.py
```

The map lists the actual cumulative implementation surface at this checkpoint. A responsibility appears only when this chapter or an earlier chapter has earned it; `ARCHITECTURE.md` and the structural tests enforce that timing.
## Run this checkpoint

Prerequisites are Python 3.11 or newer and Git. Docker is optional and used only by the Chapter 14 host-isolation probe; OPA is optional for the Chapter 20 Rego mapping.

Use the portable reader path from a fresh checkout:

```bash
git switch chapter-02
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_02.py
python -m pytest
python scripts/run_current_chapter.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The manuscript-compatible command executes the same chapter file:

```bash
python -m orders_investigation.demo chapter-02
```

Expected outcome: Orders observations are permitted; another environment, rollback, and an unknown operation are refused before outside work.

The demo opens with the building block introduced in this chapter, then shows
the real scenario, boundary decision, execution result, and what to notice.
Interactive terminals use the book's five movement colors automatically. Use
`--plain` or the `NO_COLOR` environment variable for plain text, or `--color`
to force color when output is being captured:

```bash
python scripts/run_current_chapter.py --plain
python scripts/run_current_chapter.py --color
```

Color reinforces the labels but never carries meaning alone: `APPROVED`,
`REFUSED`, and `NOT EXECUTED` remain explicit in plain output.

`uv` is optional. If it is installed, the equivalent path is:

```bash
uv sync --extra test
uv run --no-sync pytest tests/test_chapter_02.py
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The `test` extra is the portable reader contract. CI installs the all-extras superset, so optional LangGraph and HTTPX integration coverage may add checks without changing the chapter's offline acceptance result.

## Architecture evolution at this checkpoint

The tracked responsibility map now contains only the packages earned through Chapter 2. Later packages are absent from this branch.

```text
src/orders_investigation/
├── domain/
├── environment/
├── presentation/
├── runtime/
└── demo.py
```

`ARCHITECTURE.md` records only Chapters 1-2 as present evolution; `main` carries the complete roadmap.
