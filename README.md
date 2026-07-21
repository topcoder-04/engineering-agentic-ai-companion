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

This chapter needs no live model call. Its important evidence is deterministic: the exact observation result that introduces each resource identifier is retained in the trace. A failed observation cannot manufacture those identifiers.

## Deliberately incomplete

The graph can now change, but the next model turn is not yet protected against stale, malformed, or invented proposals. Chapter 5 introduces the contract between model judgment and runtime execution.

## Architecture evolution

Dependencies and readiness now form an explicit task graph. No later responsibility appears early.

```text
src/orders_investigation/
├── domain/
├── environment/
├── runtime/
├── decisions/
├── graph/
├── demo.py
└── live_demo.py
```

The real execution path follows the responsibility packages introduced through this chapter. Current packages: `domain/`, `environment/`, `runtime/`, `decisions/`, `graph/`. See `ARCHITECTURE.md`.
