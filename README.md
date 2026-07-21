# Chapter 8 companion — Trying Again Without Doing It Twice

Chapter 7 can resume after a crash. That makes a lost response dangerous: replaying the request may repeat an already committed effect. This chapter gives the intended effect a stable identity.

## What this chapter adds

- An immutable effect intent and canonical fingerprint.
- A stable idempotency key derived from run, operation, and logical attempt.
- Atomic service-side deduplication before applying the effect.
- Replay receipts for exact retries.
- A hard conflict when the same key is reused for changed intent.

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
examples/chapter_08.py
tests/test_chapter_08.py
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

The SQLite uniqueness constraint and transaction are executable evidence of the guarantee. No network or provider call is needed.

## Deliberately incomplete

Idempotency prevents duplication, but a timed-out caller still does not know whether the effect happened. Chapter 9 separates local wait outcome from outside effect outcome and reconciles the uncertainty.

## Architecture evolution

Outside effects require an idempotency boundary. No later responsibility appears early.

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
