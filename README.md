# Chapter 3 companion — When Permitted Work Still Wastes Time

The investigation boundary from Chapter 2 prevents forbidden work, but several permitted observations are ready at once. This chapter introduces a bounded model decision: the model may recommend one declared observation; it cannot execute the observation or declare the investigation complete.

## What this chapter adds

- A typed incident state with recorded and missing evidence.
- A bounded set of declared observation requests, without introducing Chapter 4's task graph.
- A provider-neutral model boundary and a deterministic fixed-choice adapter.
- A live-call receipt shape that preserves either the observed choice or the provider failure.
- A runtime boundary result kept separate from model judgment.

## Code map

```text
src/orders_investigation/__init__.py
src/orders_investigation/decisions/__init__.py
src/orders_investigation/decisions/model.py
src/orders_investigation/demo.py
src/orders_investigation/domain/__init__.py
src/orders_investigation/domain/evidence.py
src/orders_investigation/domain/incident.py
src/orders_investigation/domain/investigation.py
src/orders_investigation/environment/__init__.py
src/orders_investigation/environment/opening_case.py
src/orders_investigation/environment/requests.py
src/orders_investigation/live_demo.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
examples/chapter_03.py
tests/test_chapter_03.py
evidence/chapter-03/live-call.json
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
git switch chapter-03
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_03.py
python -m pytest
python scripts/run_current_chapter.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The manuscript-compatible command executes the same chapter file:

```bash
python -m orders_investigation.demo chapter-03
```

Expected outcome: The permitted connection-pool check closes no evidence gap; topology becomes the next useful choice.

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
uv run --no-sync pytest tests/test_chapter_03.py
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The `test` extra is the portable reader contract. CI installs the all-extras superset, so optional LangGraph and HTTPX integration coverage may add checks without changing the chapter's offline acceptance result.

## Live evidence

The deterministic adapter keeps normal use offline. A reviewed Chapter 3 receipt may be retained under `evidence/chapter-03/` with the exact scenario, instructions, raw output, parsed choice, provider/model identifiers, timing, usage, and deterministic boundary result. One receipt is evidence of one call, not a quality benchmark.

## Deliberately incomplete

The model can still return malformed, unknown, stale, or unsupported proposals. Chapter 4 lets evidence change the work graph; Chapter 5 adds the deterministic admission contract between judgment and execution.

## Architecture evolution at this checkpoint

The tracked responsibility map now contains only the packages earned through Chapter 3. Later packages are absent from this branch.

```text
src/orders_investigation/
├── domain/
├── environment/
├── presentation/
├── runtime/
├── decisions/
├── demo.py
└── live_demo.py
```

`ARCHITECTURE.md` records only Chapters 1-3 as present evolution; `main` carries the complete roadmap.
