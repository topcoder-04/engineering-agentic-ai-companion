# Chapter 13 companion — Depending on Systems That May Be Wrong

Chapter 12 exposes the next engineering pressure. This checkpoint adds evidence provenance, freshness, typed field admission, instruction-bearing content quarantine, circuit breaking, and explicit dependency failure.

## What this chapter adds

- One manuscript-aligned responsibility boundary in `src/orders_investigation/integrations/dependencies.py`.
- A deterministic, offline example that refuses an injected instruction before it reaches the decision surface.
- Exact-field and typed-value policies that keep untrusted evidence in the data plane.
- Focused failure-path tests plus every earlier chapter test inherited from `chapter-12`.
- No empty folders or placeholders for later capabilities.

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
src/orders_investigation/integrations/__init__.py
src/orders_investigation/integrations/dependencies.py
src/orders_investigation/live_demo.py
src/orders_investigation/memory/__init__.py
src/orders_investigation/memory/store.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
src/orders_investigation/runtime/contracts/__init__.py
src/orders_investigation/runtime/contracts/admission.py
src/orders_investigation/runtime/ownership.py
src/orders_investigation/runtime/workflow.py
examples/chapter_13.py
tests/test_chapter_13.py
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
## Evidence

Routine execution is offline. Historical live evidence is retained only where the manuscript uses a live model comparison; deterministic policy and failure behavior remain the acceptance authority.

## Deliberately incomplete

This branch contains only capabilities introduced through Chapter 13. Read the manuscript's closing transition for the pressure that Chapter 14 addresses.

## Architecture evolution

Dependency evidence enters through an integration contract. No later responsibility appears early.

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
├── integrations/
├── demo.py
└── live_demo.py
```

The real execution path follows the responsibility packages introduced through this chapter. Current packages: `domain/`, `environment/`, `runtime/`, `decisions/`, `graph/`, `context/`, `effects/`, `memory/`, `integrations/`. See `ARCHITECTURE.md`.

