# Chapter 10 companion — Carrying Forward Only What Helps

Chapter 9 preserves uncertain effects honestly. A long-lived investigator also needs prior lessons, but only when they are reviewed, in scope, relevant to a current gap, and small enough for the decision surface.

## What this chapter adds

- A distinct reviewed-knowledge store; retrieved lessons never become current evidence.
- Deterministic filtering by service, environment, and missing evidence.
- Text ranking only after the safety scope is fixed.
- Record and byte budgets that preserve the ranked prefix.
- A retrieval receipt containing eligible, ranked, selected, and first-omitted identities.
- Visible empty and omission outcomes instead of silent fallback.

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
src/orders_investigation/memory/__init__.py
src/orders_investigation/memory/store.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
src/orders_investigation/runtime/contracts/__init__.py
src/orders_investigation/runtime/contracts/admission.py
src/orders_investigation/runtime/workflow.py
examples/chapter_10.py
tests/test_chapter_10.py
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

The dense 500-record test proves that a budget selects only a ranked prefix. The rank-four case proves an omitted useful lesson remains diagnosable and can be recovered by changing the query or explicit budget.

## Deliberately incomplete

Useful context still does not preserve the investigation's active purpose. Chapter 11 introduces a task spine that constrains ready work to the current causal question.

## Architecture evolution

Reviewed prior knowledge needs a bounded memory boundary. No later responsibility appears early.

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
