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
scripts/run_current_chapter.py
src/orders_investigation/presentation/__init__.py
src/orders_investigation/presentation/chapters.py
src/orders_investigation/presentation/terminal.py
tests/test_demo_presentation.py
```

The map lists the actual cumulative implementation surface at this checkpoint. A responsibility appears only when this chapter or an earlier chapter has earned it; `ARCHITECTURE.md` and the structural tests enforce that timing.
## Run this checkpoint

Prerequisites are Python 3.11 or newer and Git. Docker is optional and used only by the Chapter 14 host-isolation probe; OPA is optional for the Chapter 20 Rego mapping.

Use the portable reader path from a fresh checkout:

```bash
git switch chapter-10
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_10.py
python -m pytest
python scripts/run_current_chapter.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The manuscript-compatible command executes the same chapter file:

```bash
python -m orders_investigation.demo chapter-10
```

Expected outcome: Five hundred eligible records are reduced to the ranked three-record prefix, with 497 omissions visible.

The demo opens with the building block introduced in this chapter, then shows
the real scenario, boundary decision, execution result, and what to notice.
Interactive terminals use the book's five movement colors automatically. Use
`--plain` or the `NO_COLOR` environment variable for plain text, or `--color`
to force color when output is being captured:

```bash
python scripts/run_current_chapter.py --plain
python scripts/run_current_chapter.py --color
```

Color reinforces the labels but never carries meaning alone: `APPROVED`,
`REFUSED`, and `NOT EXECUTED` remain explicit in plain output.

`uv` is optional. If it is installed, the equivalent path is:

```bash
uv sync --extra test
uv run --no-sync pytest tests/test_chapter_10.py
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The `test` extra is the portable reader contract. CI installs the all-extras superset, so optional LangGraph and HTTPX integration coverage may add checks without changing the chapter's offline acceptance result.

## Evidence

The dense 500-record test proves that a budget selects only a ranked prefix. The rank-four case proves an omitted useful lesson remains diagnosable and can be recovered by changing the query or explicit budget.

## Deliberately incomplete

Useful context still does not preserve the investigation's active purpose. Chapter 11 introduces a task spine that constrains ready work to the current causal question.

## Architecture evolution at this checkpoint

The tracked responsibility map now contains only the packages earned through Chapter 10. Later packages are absent from this branch.

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

`ARCHITECTURE.md` records only Chapters 1-10 as present evolution; `main` carries the complete roadmap.
