# Architecture evolution contract

**Current checkpoint: Chapter 12.** This document describes what is present now. It does not advertise packages from later checkpoints.

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

Responsibilities introduced after Chapter 12 are intentionally absent from this checkpoint. `main` is the complete Chapter 37 map.

## Enforced rules

1. A package appears no earlier than the chapter that earns it.
2. The README names the pressure, executable path, focused test, and expected outcome.
3. Code maps name real tracked paths; empty future packages are forbidden.
4. Generic buckets such as `helpers`, `utils`, and `misc` are forbidden.
5. Demos and tests are deterministic and offline; retained live evidence keeps provenance.
6. Adjacent chapter branches remain clean cumulative prefixes.
7. `main` moves only after all branch-local behavioral and structural gates pass.
