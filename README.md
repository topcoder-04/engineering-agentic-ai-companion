# Chapter 3 companion — When Permitted Work Still Wastes Time

The investigation boundary from Chapter 2 prevents forbidden work, but several permitted observations are ready at once. This chapter introduces a bounded model decision: the model may recommend one declared observation; it cannot execute the observation or declare the investigation complete.

## What this chapter adds

- A typed incident state with recorded and missing evidence.
- A bounded set of declared observation requests, without introducing Chapter 4's task graph.
- A provider-neutral model boundary and a deterministic fixed-choice adapter.
- A live-call receipt shape that preserves either the observed choice or the provider failure.
- A runtime boundary result kept separate from model judgment.

## Code map

```text
src/orders_investigation/__init__.py
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
src/orders_investigation/live_demo.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
examples/chapter_03.py
tests/test_chapter_03.py
evidence/chapter-03/live-call.json
```

The map lists the actual cumulative implementation surface at this checkpoint. A responsibility appears only when this chapter or an earlier chapter has earned it; `ARCHITECTURE.md` and the structural tests enforce that timing.
## Run this checkpoint

```bash
uv sync --extra test
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The full test command includes behavioral, evidence-provenance, README, and folder-evolution gates. The current demo is deterministic and offline; CI runs the same commands.
## Live evidence

The deterministic adapter keeps normal use offline. A reviewed Chapter 3 receipt may be retained under `evidence/chapter-03/` with the exact scenario, instructions, raw output, parsed choice, provider/model identifiers, timing, usage, and deterministic boundary result. One receipt is evidence of one call, not a quality benchmark.

## Deliberately incomplete

The model can still return malformed, unknown, stale, or unsupported proposals. Chapter 4 lets evidence change the work graph; Chapter 5 adds the deterministic admission contract between judgment and execution.

## Architecture evolution

Model choice now needs a provider-neutral decision seam. No later responsibility appears early.

```text
src/orders_investigation/
├── domain/
├── environment/
├── runtime/
├── decisions/
├── demo.py
└── live_demo.py
```

The real execution path follows the responsibility packages introduced through this chapter. Current packages: `domain/`, `environment/`, `runtime/`, `decisions/`. See `ARCHITECTURE.md`.
