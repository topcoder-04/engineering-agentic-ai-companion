# Chapter 12 companion — Sharing Work Without Losing Ownership

Chapter 11 keeps one investigation on course. This chapter makes the same admitted work safe to share across workers.

## What this chapter adds

- Atomic task claims with expiring leases.
- Monotonically increasing fencing tokens.
- Rejection of a stale owner's late completion.
- Backpressure through an explicit in-flight limit.

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
src/orders_investigation/effects/__init__.py
src/orders_investigation/effects/idempotency.py
src/orders_investigation/effects/reconciliation.py
src/orders_investigation/environment/__init__.py
src/orders_investigation/environment/opening_case.py
src/orders_investigation/environment/requests.py
src/orders_investigation/environment/scenario.py
src/orders_investigation/graph/__init__.py
src/orders_investigation/graph/spine.py
src/orders_investigation/graph/tasks.py
src/orders_investigation/live_demo.py
src/orders_investigation/memory/__init__.py
src/orders_investigation/memory/store.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
src/orders_investigation/runtime/contracts/__init__.py
src/orders_investigation/runtime/contracts/admission.py
src/orders_investigation/runtime/ownership.py
src/orders_investigation/runtime/workflow.py
examples/chapter_12.py
tests/test_chapter_12.py
evidence/chapter-03/live-call.json
evidence/chapter-05/live-call.json
evidence/chapter-11/current.json
evidence/chapter-11/memory.json
evidence/chapter-11/spine.json
```

The map lists the actual cumulative implementation surface at this checkpoint. A responsibility appears only when this chapter or an earlier chapter has earned it; `ARCHITECTURE.md` and the structural tests enforce that timing.
## Run this checkpoint

```bash
uv sync --extra test
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The full test command includes behavioral, evidence-provenance, README, and folder-evolution gates. The current demo is deterministic and offline; CI runs the same commands.
## Deliberately incomplete

Ownership is now safe, but the dependency a worker calls may still return stale, partial, or unattributable evidence. Chapter 13 adds evidence-admission rules and dependency failure control.

## Architecture evolution

Concurrent work needs explicit runtime ownership. No later responsibility appears early.

```text
src/orders_investigation/
├── domain/
├── environment/
├── runtime/
├── decisions/
├── graph/
├── context/
├── effects/
├── memory/
├── demo.py
└── live_demo.py
```

The real execution path follows the responsibility packages introduced through this chapter. Current packages: `domain/`, `environment/`, `runtime/`, `decisions/`, `graph/`, `context/`, `effects/`, `memory/`. See `ARCHITECTURE.md`.
