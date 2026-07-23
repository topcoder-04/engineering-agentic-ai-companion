# Chapter 37 companion — Making Risk Posture an Engineering Contract

Chapter 36 made platform evolution compatible. This final checkpoint makes the
launch posture executable: the candidate may run only when the proof chain
matches its consequence and every hard obligation remains satisfied.

## What this chapter adds

- Consequence-selected risk tiers and independent hard launch vetoes live in
  `platform/risk/`.
- Launch evidence is derived from executed variations, lifecycle ownership,
  artifact-bound conformance, caller authorization, and data-safe placement.
- The complete demo follows one accepted candidate through the assembled system,
  then removes one proof at a time and shows six exact refusals.

## Code map

```text
src/orders_investigation/platform/risk/__init__.py
src/orders_investigation/runtime/journey.py
src/orders_investigation/presentation/__init__.py
src/orders_investigation/presentation/chapters.py
src/orders_investigation/presentation/terminal.py
examples/chapter_37.py
tests/test_chapter_37.py
tests/test_demo_presentation.py
scripts/run_current_chapter.py
scripts/validate_evidence.py
```

The map names the Chapter 37 delta and the shared surfaces that make its
behavior visible. Every earlier responsibility remains executable through the
cumulative suite.

## Run this checkpoint

Prerequisites are Python 3.11 or newer and Git. Docker is optional and used only by the Chapter 14 host-isolation probe; OPA is optional for the Chapter 20 Rego mapping.

Use the portable reader path from a fresh checkout:

```bash
git switch chapter-37
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_37.py
python -m pytest
python scripts/run_current_chapter.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The manuscript-compatible command executes the same chapter file:

```bash
python -m orders_investigation.demo chapter-37
```

Expected outcome: Complete launch evidence passes; six separate candidates each remove one required proof, produce exactly one launch veto, and show NOT EXECUTED.

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
uv run --no-sync pytest tests/test_chapter_37.py
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The `test` extra is the portable reader contract. CI installs the all-extras superset, so optional LangGraph and HTTPX integration coverage may add checks without changing the chapter's offline acceptance result.

## Architecture evolution at this checkpoint

The tracked responsibility map now contains only the packages earned through Chapter 37. Later packages are absent from this branch.

```text
src/orders_investigation/
├── domain/
├── environment/
├── presentation/
├── runtime/
├── decisions/
├── graph/
├── context/
├── effects/
├── memory/
├── integrations/
├── coordination/
├── governance/
├── evaluation/
├── operations/
├── platform/
│   ├── identity/
│   ├── capabilities/
│   ├── authority/
│   ├── placement/
│   ├── defaults/
│   ├── releases/
│   ├── lifecycle/
│   ├── compatibility/
│   └── risk/
├── demo.py
└── live_demo.py
```

`ARCHITECTURE.md` records only Chapters 1-37 as present evolution; `main` carries the complete roadmap.
