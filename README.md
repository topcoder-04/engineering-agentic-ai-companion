# Chapter 33 companion — Making the Safe Path the Easy Path

This checkpoint adds platform scaffolding with visible, declared escape hatches.

## What this chapter adds

- Safe project scaffolding and scaffold admission live in `platform/defaults/`.
- The paved Orders project shape feeds the placement-, authority-, capability-, and identity-gated journey.
- A composition test proves an unapproved override cannot launch work.

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
src/orders_investigation/platform/authority/__init__.py
src/orders_investigation/platform/capabilities/__init__.py
src/orders_investigation/platform/controls.py
src/orders_investigation/platform/defaults/__init__.py
src/orders_investigation/platform/identity/__init__.py
src/orders_investigation/platform/placement/__init__.py
src/orders_investigation/runtime/__init__.py
src/orders_investigation/runtime/boundary.py
src/orders_investigation/runtime/contracts/__init__.py
src/orders_investigation/runtime/contracts/admission.py
src/orders_investigation/runtime/journey.py
src/orders_investigation/runtime/ownership.py
src/orders_investigation/runtime/sandbox.py
src/orders_investigation/runtime/workflow.py
examples/chapter_33.py
tests/test_chapter_33.py
evidence/chapter-03/live-call.json
evidence/chapter-05/live-call.json
evidence/chapter-11/current.json
evidence/chapter-11/memory.json
evidence/chapter-11/spine.json
evidence/chapter-14/docker-isolation.json
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
git switch chapter-33
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_33.py
python -m pytest
python scripts/run_current_chapter.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The manuscript-compatible command executes the same chapter file:

```bash
python -m orders_investigation.demo chapter-33
```

Expected outcome: The paved path generates agent.yaml, its conformance test, and runbook.md with no exceptions.

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
uv run --no-sync pytest tests/test_chapter_33.py
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The `test` extra is the portable reader contract. CI installs the all-extras superset, so optional LangGraph and HTTPX integration coverage may add checks without changing the chapter's offline acceptance result.

## Behavioral spine

The paved path is now the build-time entrance to the same runtime spine. Its contract,
conformance test, and runbook allow the Orders project to proceed through placement
and execute. Adding `custom/router.py` records an exception; without explicit
approval, scaffold admission refuses the project before launch.
## Deliberately incomplete

This branch contains no platform capability introduced after Chapter 33. Chapter 34 addresses the next manuscript pressure.

## Architecture evolution at this checkpoint

The tracked responsibility map now contains only the packages earned through Chapter 33. Later packages are absent from this branch.

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

`ARCHITECTURE.md` records only Chapters 1-33 as present evolution; `main` carries the complete roadmap.
