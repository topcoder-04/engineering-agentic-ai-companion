# Chapter 2 — What This Investigation May Touch

This cumulative checkpoint implements only the boundary earned by Chapter 2; all earlier behavior remains executable.

## What changes here

- `ARCHITECTURE.md`
- `src/orders_investigation/__init__.py`
- `src/orders_investigation/demo.py`
- `src/orders_investigation/domain/__init__.py`
- `src/orders_investigation/domain/evidence.py`
- `src/orders_investigation/domain/investigation.py`
- `src/orders_investigation/environment/__init__.py`
- `src/orders_investigation/environment/opening_case.py`
- `src/orders_investigation/environment/requests.py`
- `src/orders_investigation/runtime/__init__.py`
- `src/orders_investigation/runtime/boundary.py`
- `tests/test_chapter_01.py`
- `tests/test_chapter_02.py`

## Code map

```text
src/orders_investigation/__init__.py
src/orders_investigation/demo.py
src/orders_investigation/domain/__init__.py
src/orders_investigation/domain/evidence.py
src/orders_investigation/domain/investigation.py
src/orders_investigation/environment/__init__.py
src/orders_investigation/environment/opening_case.py
src/orders_investigation/environment/requests.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
examples/chapter_02.py
tests/test_chapter_02.py
```

The map lists the actual cumulative implementation surface at this checkpoint. A responsibility appears only when this chapter or an earlier chapter has earned it; `ARCHITECTURE.md` and the structural tests enforce that timing.
## Run this checkpoint

```bash
uv sync --extra test
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The full test command includes behavioral, evidence-provenance, and structural gates. The demo is deterministic and offline. CI runs the same commands.
