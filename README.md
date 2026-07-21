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

No live call is required. Deterministic attempt fixtures prove timeout, exhaustion, usage accounting, and the absence of fabricated judgment.

## Deliberately incomplete

The ledger exists only in process. Chapter 7 persists the changing investigation, graph, and decision history so a restart can resume the same work.

## Architecture evolution

Judgment limits become an explicit decision dependency. No later responsibility appears early.

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
