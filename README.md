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
git switch chapter-05
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_05.py
python -m pytest
python scripts/run_current_chapter.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The manuscript-compatible command executes the same chapter file:

```bash
python -m orders_investigation.demo chapter-05
```

Expected outcome: The pipeline proposal is admitted, while its unsupported parallelism reason remains outside evidence.

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
uv run --no-sync pytest tests/test_chapter_05.py
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The `test` extra is the portable reader contract. CI installs the all-extras superset, so optional LangGraph and HTTPX integration coverage may add checks without changing the chapter's offline acceptance result.

## Evidence

The earlier live-call receipt for this decision is retained as historical evidence when published. Tests remain offline and prove the post-response admission result independently of the provider.

## Deliberately incomplete

Admission protects one proposal, but repeated model calls can still consume unbounded time and tokens. Chapter 6 gives judgment an explicit budget and records failed attempts without inventing a choice.

## Architecture evolution at this checkpoint

The tracked responsibility map now contains only the packages earned through Chapter 5. Later packages are absent from this branch.

```text
src/orders_investigation/
├── domain/
├── environment/
├── presentation/
├── runtime/
├── decisions/
├── graph/
├── context/
├── demo.py
└── live_demo.py
```

`ARCHITECTURE.md` records only Chapters 1-5 as present evolution; `main` carries the complete roadmap.
