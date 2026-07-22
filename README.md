# Chapter 29 companion — Making an Agent Identifiable

This checkpoint adds immutable, owned, versioned agent contracts in a registry.

## What this chapter adds

- Immutable workload contracts live in `platform/identity/`; `platform/controls.py` is compatibility-only.
- The shared Orders journey now resolves the exact registered agent version before doing work.
- A composition test proves an unknown version cannot start the investigation.

## Code map

```text
src/orders_investigation/__init__.py
src/orders_investigation/context/__init__.py
src/orders_investigation/context/surface.py
src/orders_investigation/coordination/__init__.py
src/orders_investigation/coordination/delegation.py
src/orders_investigation/decisions/__init__.py
src/orders_investigation/decisions/budget.py
src/orders_investigation/decisions/model.py
src/orders_investigation/decisions/routing.py
src/orders_investigation/demo.py
src/orders_investigation/domain/__init__.py
src/orders_investigation/domain/evidence.py
src/orders_investigation/domain/incident.py
src/orders_investigation/domain/investigation.py
src/orders_investigation/effects/__init__.py
src/orders_investigation/effects/enforcement.py
src/orders_investigation/effects/idempotency.py
src/orders_investigation/effects/reconciliation.py
src/orders_investigation/environment/__init__.py
src/orders_investigation/environment/opening_case.py
src/orders_investigation/environment/requests.py
src/orders_investigation/environment/scenario.py
src/orders_investigation/evaluation/__init__.py
src/orders_investigation/evaluation/production.py
src/orders_investigation/governance/__init__.py
src/orders_investigation/governance/approval.py
src/orders_investigation/governance/authority.py
src/orders_investigation/governance/policy.py
src/orders_investigation/graph/__init__.py
src/orders_investigation/graph/planning.py
src/orders_investigation/graph/spine.py
src/orders_investigation/graph/tasks.py
src/orders_investigation/integrations/__init__.py
src/orders_investigation/integrations/dependencies.py
src/orders_investigation/live_demo.py
src/orders_investigation/memory/__init__.py
src/orders_investigation/memory/store.py
src/orders_investigation/operations/__init__.py
src/orders_investigation/operations/fleet.py
src/orders_investigation/operations/learning.py
src/orders_investigation/operations/observability.py
src/orders_investigation/operations/probes.py
src/orders_investigation/platform/__init__.py
src/orders_investigation/platform/controls.py
src/orders_investigation/platform/identity/__init__.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
src/orders_investigation/runtime/contracts/__init__.py
src/orders_investigation/runtime/contracts/admission.py
src/orders_investigation/runtime/journey.py
src/orders_investigation/runtime/ownership.py
src/orders_investigation/runtime/sandbox.py
src/orders_investigation/runtime/workflow.py
examples/chapter_29.py
tests/test_chapter_29.py
evidence/chapter-03/live-call.json
evidence/chapter-05/live-call.json
evidence/chapter-11/current.json
evidence/chapter-11/memory.json
evidence/chapter-11/spine.json
evidence/chapter-14/docker-isolation.json
```

The map lists the actual cumulative implementation surface at this checkpoint. A responsibility appears only when this chapter or an earlier chapter has earned it; `ARCHITECTURE.md` and the structural tests enforce that timing.
## Run this checkpoint

```bash
uv sync --extra test
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The full test command includes behavioral, evidence-provenance, README, and folder-evolution gates. The current demo is deterministic and offline; CI runs the same commands.

## Behavioral spine

Identity no longer floats beside the agent. The Orders composition root resolves an
immutable `orders-investigator` contract before entering the investigation path. The
registered version completes the report effect; an unknown version is refused before
the first observation, proposal, or write.
## Deliberately incomplete

This branch contains no platform capability introduced after Chapter 29. Chapter 30 addresses the next manuscript pressure.

## Architecture evolution

Stable agent identity begins the platform map. No later platform responsibility appears early.

```text
src/orders_investigation/platform/
├── controls.py
├── identity/
```

The platform map now exposes `identity/`. Each subdomain is introduced only when its contract becomes executable. See `ARCHITECTURE.md`.
