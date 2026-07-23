# Chapter 6 companion — When Judgment Becomes a Dependency

Chapter 5 safely admits a returned proposal. This chapter makes the attempt to obtain that proposal bounded and observable.

## What this chapter adds

- A per-investigation decision budget for calls, retries, time, and usage.
- An append-only ledger of successful and failed model attempts.
- Explicit stop reasons when judgment is unavailable or exhausted.
- A fail-closed rule: timeout and unavailable attempts cannot contain a choice.

## Code map

```text
src/orders_investigation/__init__.py
src/orders_investigation/context/__init__.py
src/orders_investigation/context/surface.py
src/orders_investigation/decisions/__init__.py
src/orders_investigation/decisions/budget.py
src/orders_investigation/decisions/model.py
src/orders_investigation/demo.py
src/orders_investigation/domain/__init__.py
src/orders_investigation/domain/evidence.py
src/orders_investigation/domain/incident.py
src/orders_investigation/domain/investigation.py
src/orders_investigation/environment/__init__.py
src/orders_investigation/environment/opening_case.py
src/orders_investigation/environment/requests.py
src/orders_investigation/environment/scenario.py
src/orders_investigation/graph/__init__.py
src/orders_investigation/graph/tasks.py
src/orders_investigation/live_demo.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
src/orders_investigation/runtime/contracts/__init__.py
src/orders_investigation/runtime/contracts/admission.py
examples/chapter_06.py
tests/test_chapter_06.py
evidence/chapter-03/live-call.json
evidence/chapter-05/live-call.json
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
git switch chapter-06
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_06.py
python -m pytest
python scripts/run_current_chapter.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The manuscript-compatible command executes the same chapter file:

```bash
python -m orders_investigation.demo chapter-06
```

Expected outcome: Two timed-out attempts consume 8,000 ms, return no choice, and stop with model_timeout.

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
uv run --no-sync pytest tests/test_chapter_06.py
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The `test` extra is the portable reader contract. CI installs the all-extras superset, so optional LangGraph and HTTPX integration coverage may add checks without changing the chapter's offline acceptance result.

## Evidence

No live call is required. Deterministic attempt fixtures prove timeout, exhaustion, usage accounting, and the absence of fabricated judgment.

## Deliberately incomplete

The ledger exists only in process. Chapter 7 persists the changing investigation, graph, and decision history so a restart can resume the same work.

## Architecture evolution at this checkpoint

The tracked responsibility map now contains only the packages earned through Chapter 6. Later packages are absent from this branch.

```text
src/orders_investigation/
├── domain/
├── environment/
├── presentation/
├── runtime/
├── decisions/
├── graph/
├── context/
├── demo.py
└── live_demo.py
```

`ARCHITECTURE.md` records only Chapters 1-6 as present evolution; `main` carries the complete roadmap.
