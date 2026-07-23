# Architecture evolution contract

**Current checkpoint: Chapter 33.** This document describes what is present now. It does not advertise packages from later checkpoints.

## Present responsibility map

```text
src/orders_investigation/
├── domain/
├── environment/
├── presentation/
├── runtime/
├── decisions/
├── graph/
├── context/
├── effects/
├── memory/
├── integrations/
├── coordination/
├── governance/
├── evaluation/
├── operations/
├── platform/
│   ├── identity/
│   ├── capabilities/
│   ├── authority/
│   ├── placement/
│   └── defaults/
├── demo.py
└── live_demo.py
```

## Evolution earned so far

| Chapter | Boundary introduced | Why it appears here |
|---:|---|---|
| 1 | `domain/`, `environment/`, `presentation/` | Separate completion facts from outside observations and effects, then render their proof consistently. |
| 2 | `runtime/boundary.py` | Declare what the investigation may observe or change. |
| 3 | `decisions/model.py` | Keep probabilistic choice behind a provider-neutral seam. |
| 4 | `graph/tasks.py` | Let recorded evidence create concrete dependent work. |
| 5 | `context/`, `runtime/contracts/` | Separate the model-visible surface, proposal admission, and execution. |
| 6 | `decisions/budget.py` | Make variable judgment a bounded dependency. |
| 7 | `runtime/workflow.py` | Persist changed work and charged attempts across restart. |
| 8 | `effects/idempotency.py` | Give a consequential effect stable identity. |
| 9 | `effects/reconciliation.py` | Preserve unknown outcomes until effect truth is recovered. |
| 10 | `memory/` | Admit only reviewed, scoped, bounded prior knowledge. |
| 11 | `graph/spine.py` | Constrain ready work to the active causal question. |
| 12 | `runtime/ownership.py` | Lease work while fencing stale completion. |
| 13 | `integrations/` | Admit typed dependency results at the source boundary. |
| 14 | `runtime/sandbox.py` | Run generated analysis inside an isolated, artifact-checked boundary. |
| 15 | `decisions/routing.py` | Match judgment consequence to a compatible source. |
| 16 | `graph/planning.py` | Replace future commitments without rewriting succeeded history. |
| 17 | `coordination/` | Join exact delegated returns under one owner. |
| 18 | `governance/approval.py` | Persist and correlate consequential approval. |
| 19 | `governance/authority.py` | Bind verified identity to one exact delegated grant. |
| 20 | `governance/policy.py` | Decide from structured facts rather than wording. |
| 21 | `effects/enforcement.py`, `runtime/journey.py` | Recheck policy at the effect and compose the cumulative Orders path. |
| 22 | `evaluation/` | Preserve the semantic trajectory needed for judgment. |
| 23 | `evaluation/production.py` | Evaluate outcomes and path dimensions together. |
| 24 | `evaluation/production.py` release gate | Turn evaluation evidence into a fail-closed release decision. |
| 25 | `operations/observability.py` | Expose useful production fields without raw content. |
| 26 | `operations/probes.py` | Exercise deliberate model, dependency, and timing variations. |
| 27 | `operations/learning.py` | Promote incident failures into owned regression boundaries. |
| 28 | `operations/fleet.py` | Route released candidates within shared cell limits. |
| 29 | `platform/identity/` | Resolve every agent version to an immutable contract. |
| 30 | `platform/capabilities/` | Admit compatible capabilities instead of copying settings. |
| 31 | `platform/authority/` | Carry caller authority without becoming a confused deputy. |
| 32 | `platform/placement/` | Make tenant, residency, data class, and retention structural. |
| 33 | `platform/defaults/` | Make the safe platform path the easiest path. |

Responsibilities introduced after Chapter 33 are intentionally absent from this checkpoint. `main` is the complete Chapter 37 map.

## Enforced rules

1. A package appears no earlier than the chapter that earns it.
2. The README names the pressure, executable path, focused test, and expected outcome.
3. Code maps name real tracked paths; empty future packages are forbidden.
4. Generic buckets such as `helpers`, `utils`, and `misc` are forbidden.
5. Demos and tests are deterministic and offline; retained live evidence keeps provenance.
6. Adjacent chapter branches remain clean cumulative prefixes.
7. `main` moves only after all branch-local behavioral and structural gates pass.
