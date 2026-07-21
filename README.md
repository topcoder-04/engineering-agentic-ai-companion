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
```

The map lists the actual cumulative implementation surface at this checkpoint. A responsibility appears only when this chapter or an earlier chapter has earned it; `ARCHITECTURE.md` and the structural tests enforce that timing.
## Run this checkpoint

```bash
uv sync --extra test
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The full test command includes behavioral, evidence-provenance, README, and folder-evolution gates. The current demo is deterministic and offline; CI runs the same commands.
## Evidence

Restart behavior is demonstrated with a real SQLite file in the tests. The optional LangGraph adapter executes only when its packages are installed; the local deterministic store remains the architectural contract.

## Deliberately incomplete

A resumed process may retry a consequential request whose first response was lost. Chapter 8 gives that effect a stable identity so a retry cannot apply it twice.

## Architecture evolution

Changed work must survive restart. No later responsibility appears early.

```text
src/orders_investigation/
├── domain/
├── environment/
├── runtime/
├── decisions/
├── graph/
├── context/
├── demo.py
└── live_demo.py
```

The real execution path follows the responsibility packages introduced through this chapter. Current packages: `domain/`, `environment/`, `runtime/`, `decisions/`, `graph/`, `context/`. See `ARCHITECTURE.md`.
