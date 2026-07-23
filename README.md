# Chapter 7 companion — Keeping Changed Work Alive After a Restart

Chapter 6 records model attempts, but an in-memory investigation disappears with its process. This chapter gives the run a durable identity and checkpoint.

## What this chapter adds

- A file-backed SQLite run store keyed by `run_id`.
- Round-trip persistence for incident evidence, graph state, hypothesis revisions, and the decision ledger.
- A restart demonstration that closes and reopens the database.
- A complete controlled-turn graph whose nodes retain their original responsibilities.
- Honest crash semantics: a checkpoint cannot invent an outside effect result it never observed.

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
src/orders_investigation/runtime/workflow.py
examples/chapter_07.py
tests/test_chapter_07.py
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
git switch chapter-07
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_07.py
python -m pytest
python scripts/run_current_chapter.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The manuscript-compatible command executes the same chapter file:

```bash
python -m orders_investigation.demo chapter-07
```

The Part 1 interlude replay is also executable:

```bash
python -m orders_investigation.demo foundation-replay
```

Expected outcome: The changed graph, recorded evidence, and one charged model attempt survive restoration.

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
uv run --no-sync pytest tests/test_chapter_07.py
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The `test` extra is the portable reader contract. CI installs the all-extras superset, so optional LangGraph and HTTPX integration coverage may add checks without changing the chapter's offline acceptance result.

## Evidence

Restart behavior is demonstrated with a real SQLite file in the tests. The optional LangGraph adapter executes only when its packages are installed; the local deterministic store remains the architectural contract.

## Deliberately incomplete

A resumed process may retry a consequential request whose first response was lost. Chapter 8 gives that effect a stable identity so a retry cannot apply it twice.

## Architecture evolution at this checkpoint

The tracked responsibility map now contains only the packages earned through Chapter 7. Later packages are absent from this branch.

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

`ARCHITECTURE.md` records only Chapters 1-7 as present evolution; `main` carries the complete roadmap.
