# Chapter 4 companion — When Evidence Changes the Shape of the Work

Chapter 3 could choose among the observations already visible. That is not enough once topology evidence reveals resources that were previously unknown. This chapter makes the work graph expand only from recorded evidence.

## What this chapter adds

- Explicit `waiting`, `ready`, `succeeded`, and `failed` task states.
- Dependencies that keep newly discovered work blocked until its prerequisite succeeds.
- Evidence-driven expansion from topology, to writer activity, to migration, to deployment.
- A recorded hypothesis revision that must name evidence the incident actually holds.
- Failure behavior: an unsuccessful topology observation creates no endpoint work.

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
src/orders_investigation/graph/__init__.py
src/orders_investigation/graph/tasks.py
src/orders_investigation/live_demo.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
examples/chapter_04.py
tests/test_chapter_04.py
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
git switch chapter-04
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_04.py
python -m pytest
python scripts/run_current_chapter.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The manuscript-compatible command executes the same chapter file:

```bash
python -m orders_investigation.demo chapter-04
```

Expected outcome: Topology creates writer and replica work; writer and migration evidence create the pipeline task.

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
uv run --no-sync pytest tests/test_chapter_04.py
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The `test` extra is the portable reader contract. CI installs the all-extras superset, so optional LangGraph and HTTPX integration coverage may add checks without changing the chapter's offline acceptance result.

## Evidence

This chapter needs no live model call. Its important evidence is deterministic: the exact observation result that introduces each resource identifier is retained in the trace. A failed observation cannot manufacture those identifiers.

## Deliberately incomplete

The graph can now change, but the next model turn is not yet protected against stale, malformed, or invented proposals. Chapter 5 introduces the contract between model judgment and runtime execution.

## Architecture evolution at this checkpoint

The tracked responsibility map now contains only the packages earned through Chapter 4. Later packages are absent from this branch.

```text
src/orders_investigation/
├── domain/
├── environment/
├── presentation/
├── runtime/
├── decisions/
├── graph/
├── demo.py
└── live_demo.py
```

`ARCHITECTURE.md` records only Chapters 1-4 as present evolution; `main` carries the complete roadmap.
