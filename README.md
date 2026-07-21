# Chapter 5 companion — What the Model Sees and What May Run

Chapter 4 can discover new work, but a model response is still only text. This chapter introduces the contract that turns a current, well-formed, permitted proposal into a runtime invocation.

## What this chapter adds

- One honest decision surface built from current incident and graph state.
- A typed `Proposal` that rejects missing, extra, or malformed fields.
- The optional OpenAI adapter requests that exact schema through `responses.parse` and consumes `output_parsed`.
- Runtime admission that resolves the task again, checks readiness, and checks the deterministic boundary.
- A strict separation between a model's reason and recorded evidence.
- Refusal of stale or unknown proposals before execution.

## Code map

```text
src/orders_investigation/__init__.py
src/orders_investigation/context/__init__.py
src/orders_investigation/context/surface.py
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
src/orders_investigation/environment/scenario.py
src/orders_investigation/graph/__init__.py
src/orders_investigation/graph/tasks.py
src/orders_investigation/live_demo.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
src/orders_investigation/runtime/contracts/__init__.py
src/orders_investigation/runtime/contracts/admission.py
examples/chapter_05.py
tests/test_chapter_05.py
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

The earlier live-call receipt for this decision is retained as historical evidence when published. Tests remain offline and prove the post-response admission result independently of the provider.

## Deliberately incomplete

Admission protects one proposal, but repeated model calls can still consume unbounded time and tokens. Chapter 6 gives judgment an explicit budget and records failed attempts without inventing a choice.

## Architecture evolution

Model-visible context, typed proposals, admission, and execution now need separate homes. No later responsibility appears early.

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
