# Chapter 9 companion — When an Attempt Ends but Its Effect Is Unknown

Chapter 8 prevents duplicate effects. It does not let a caller infer an outside result from a local timeout. This chapter models those two lifecycles separately.

## What this chapter adds

- Separate wait and effect outcomes on every attempt.
- `not_dispatched`, `unknown`, `succeeded`, and `failed` effect states.
- A local timeout that stops waiting without pretending to cancel the outside work.
- Durable attempt records keyed by the same idempotency identity.
- Reconciliation that queries the effect service and preserves `unknown` when proof is absent.

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
src/orders_investigation/graph/tasks.py
src/orders_investigation/live_demo.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
src/orders_investigation/runtime/contracts/__init__.py
src/orders_investigation/runtime/contracts/admission.py
src/orders_investigation/runtime/workflow.py
examples/chapter_09.py
tests/test_chapter_09.py
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

The async test deliberately times out before the service finishes, proves the outside task continues, reopens the database, and reconciles to the service receipt.

## Deliberately incomplete

The investigation can now survive uncertainty, but long runs still need useful prior lessons without confusing them with present evidence. Chapter 10 adds scoped, reviewed, bounded retrieval.

## Architecture evolution

Unknown outside outcomes require reconciliation. No later responsibility appears early.

```text
src/orders_investigation/
├── domain/
├── environment/
├── runtime/
├── decisions/
├── graph/
├── context/
├── effects/
├── demo.py
└── live_demo.py
```

The real execution path follows the responsibility packages introduced through this chapter. Current packages: `domain/`, `environment/`, `runtime/`, `decisions/`, `graph/`, `context/`, `effects/`. See `ARCHITECTURE.md`.
