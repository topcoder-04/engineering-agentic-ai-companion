# Engineering Agentic AI — executable companion

This repository is the working system behind *Engineering Agentic AI: From Useful Answers to Dependable Work*. It is organized as 37 cumulative checkpoints: each `chapter-NN` branch is a true prefix of the final system, and `main` is the complete Chapter 37 journey.

The model may be flexible because the boundary is not. Every checkpoint keeps the model-facing choice separate from deterministic admission, evidence provenance, effect identity, evaluation, and platform governance.

## Explore the agent's evolution

See the system grow from a useful answer in Chapter 1 to an operable platform in
Chapter 37:

- [Open the animated single-screen guide](https://htmlpreview.github.io/?https://github.com/topcoder-04/engineering-agentic-ai-companion/blob/main/docs/miras-journey.html)
  — it starts at Chapter 1 and builds the system automatically, one boundary at
  a time. Pause at any point or use the arrows to move at your own pace.
- [Download the self-contained guide](docs/miras-journey.html?raw=1) — open it
  locally when you want the same experience offline.
- [Read the chapter reference](docs/MIRAS_JOURNEY.md) — the non-animated index
  with links to every executable checkpoint.
- [Record the narrative voice-over](docs/miras-journey-voiceover.md) — a timed,
  human-paced script that follows the same Orders incident across the complete
  9:18 journey.

The simulation is a read-only map of the manuscript responsibilities and
executable checkpoint boundaries; it runs no repository code or tests. Each
chapter reveals a connected component only when the journey earns it. After
playback, any built chapter can be selected to inspect the addition and the new
refusal it made executable.

## Start here

Prerequisites:

- Python 3.11 or newer
- Git
- [uv](https://docs.astral.sh/uv/) is optional
- Docker only for the Chapter 14 isolation probe
- OPA only for the Chapter 20 Rego example

Choose the chapter you are reading and use the portable reader path:

```bash
git switch chapter-05
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_05.py
python -m pytest
python scripts/run_current_chapter.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The first
command changes the implementation, README, and architecture map to the state
earned by that chapter. Tests are cumulative: Chapter 13 runs Chapters 1–13,
never a disconnected sample.

For the complete system on `main`:

```bash
git switch main
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_37.py
python -m pytest
python scripts/run_current_chapter.py
python scripts/validate_evidence.py
```

The manuscript-compatible command executes the same Chapter 37 file:

```bash
python -m orders_investigation.demo chapter-37
```

Expected outcome: complete launch evidence passes, the integrated Orders path
executes once, then six separate candidates each remove one required proof.
Insufficient evaluation, a safety failure, missing ownership, unproven rollback,
unproven caller authority, and an unproven data boundary each produce exactly
one launch veto and print `executed False`.

`uv` is optional. If it is installed, the equivalent reader path is:

```bash
uv sync --extra test
uv run --no-sync pytest tests/test_chapter_37.py
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
uv run --no-sync python scripts/validate_evidence.py
```

The main demo executes both sides of the final boundary. Its accepted candidate is
identified, capability-admitted, scaffolded, conformance-bound, owned,
compatibility-checked, caller-authorized, placed, evaluated across variations, and
risk-approved before the Orders investigation writes its report. Its refused
candidates each remove one required proof, receive exactly one launch veto, and
never execute.

The `test` extra is the portable reader contract. CI installs the all-extras
superset, so optional LangGraph and HTTPX integration coverage may add checks
without changing the offline acceptance result.

## One executable journey

The late chapters tighten two connected paths rather than adding neighboring APIs:

```text
release: identity → capability → scaffold → conformance → ownership → compatibility → risk
runtime: caller authority → placement → observe → propose → admit → effect → trace → evaluate
feedback: evaluation → release gate → fleet → incident regression → next launch
```

`src/orders_investigation/runtime/journey.py` is the composition root. Responsibility
packages remain independent; this file carries their real receipts, decisions, and
refusals into the next boundary.

## Dependency profiles

The offline project does not require an OpenAI SDK, LangGraph, or its SQLite checkpointer. Install only the surface you want:

| Extra | Purpose |
|---|---|
| `test` | Offline behavioral and structural verification |
| `live` | Optional OpenAI live comparison |
| `langgraph` | Optional LangGraph execution and SQLite checkpoint integration |
| `integrations` | Optional HTTP dependency adapter |
| `--all-extras` | CI and full maintainer verification |

## The checkpoint journey

| Branch | Capability introduced |
|---|---|
| `chapter-01` | Separate a useful answer from completed work |
| `chapter-02` | Bound what the investigation may touch |
| `chapter-03` | Separate model choice from permitted execution |
| `chapter-04` | Expand work from recorded evidence |
| `chapter-05` | Admit a schema-validated model proposal |
| `chapter-06` | Budget variable judgment |
| `chapter-07` | Persist and resume the controlled workflow |
| `chapter-08` | Retry without duplicating an effect |
| `chapter-09` | Reconcile an effect whose outcome is unknown |
| `chapter-10` | Retrieve only relevant, bounded memory |
| `chapter-11` | Keep the investigation on an explicit task spine |
| `chapter-12` | Delegate work without losing ownership |
| `chapter-13` | Admit typed dependency evidence and quarantine instruction-bearing content |
| `chapter-14` | Execute generated work inside a sandbox |
| `chapter-15` | Match decision consequence to required judgment |
| `chapter-16` | Replan when evidence changes the next useful action |
| `chapter-17` | Merge contributions without confusing them for completion |
| `chapter-18` | Wait safely for consequential approval |
| `chapter-19` | Bind authority to explicit capabilities |
| `chapter-20` | Express policy independently of model wording |
| `chapter-21` | Enforce policy where effects occur |
| `chapter-22` | Trace the path, not only the answer |
| `chapter-23` | Evaluate the complete trajectory |
| `chapter-24` | Make evaluation a release boundary |
| `chapter-25` | Observe production without exposing sensitive content |
| `chapter-26` | Test variations authored cases miss |
| `chapter-27` | Turn incident lessons into executable boundaries |
| `chapter-28` | Operate a fleet within shared limits |
| `chapter-29` | Give every agent a verifiable identity |
| `chapter-30` | Admit capabilities instead of copying settings |
| `chapter-31` | Carry the caller's authority without becoming a confused deputy |
| `chapter-32` | Keep tenant data inside its boundary |
| `chapter-33` | Make the safe platform path the easy path |
| `chapter-34` | Bind conformance evidence to the released artifact |
| `chapter-35` | Preserve ownership after launch |
| `chapter-36` | Evolve platform contracts through compatibility windows |
| `chapter-37` | Make launch risk an executable engineering contract |

## Repository map

```text
src/orders_investigation/domain/
src/orders_investigation/environment/
src/orders_investigation/runtime/
src/orders_investigation/runtime/journey.py
src/orders_investigation/decisions/
src/orders_investigation/graph/
src/orders_investigation/context/
src/orders_investigation/effects/
src/orders_investigation/memory/
src/orders_investigation/integrations/
src/orders_investigation/coordination/
src/orders_investigation/governance/
src/orders_investigation/evaluation/
src/orders_investigation/operations/
src/orders_investigation/platform/
docs/MIRAS_JOURNEY.md
docs/miras-journey.html
examples/chapter_37.py
tests/test_chapter_37.py
```

`ARCHITECTURE.md` records when each responsibility folder is allowed to appear. `tests/test_folder_birth.py` enforces that schedule on every branch.

## Evidence and provenance

`evidence/` contains retained observations used by the manuscript. A retained file is not accepted merely because it exists: `scripts/validate_evidence.py` checks its source kind, timestamp, scenario, and deterministic result. Current retained evidence includes:

- observed model comparisons for Chapters 3 and 5;
- current, memory, and task-spine comparisons for Chapter 11;
- the Docker isolation probe for Chapter 14.

Offline fixtures remain the acceptance authority. Live calls are comparative evidence, not an undocumented prerequisite.

## Chapter 37 completion boundary

The final checkpoint combines workload identity, capability admission, delegated caller authority, tenant placement, paved defaults, release receipts, lifecycle ownership, compatibility windows, and risk-tier launch decisions. `LaunchEvidence` is derived from executed variation results, lifecycle validation, the artifact-bound conformance receipt, caller authorization, and the selected data-safe target. No hand-built launch boolean can bypass those producers. It is complete only when the cumulative tests, structural gates, integrated success-and-refusal demo, and retained-evidence validation all pass.
