# Architecture evolution contract

The repository tree is part of the teaching. A responsibility becomes a package only when the manuscript creates enough pressure to justify it. Earlier branches do not contain empty future packages.

| Chapter | Boundary introduced | Why it appears here |
|---:|---|---|
| 1 | `domain/`, `environment/` | Separate the goal and evidence from outside observations and effects. |
| 2 | `runtime/boundary.py` | Declare what the investigation may observe or change. |
| 3 | `decisions/model.py` | Keep probabilistic choice behind a provider-neutral seam. |
| 4 | `graph/tasks.py` | Make dependencies, readiness, and evidence-driven expansion visible. |
| 5 | `runtime/contracts/`, `context/` | Separate model-visible context, proposals, admission, and execution. |
| 6 | `decisions/budget.py` | Bound judgment as an explicit dependency. |
| 7 | `runtime/workflow.py` | Persist changed work and resume it safely. |
| 8–9 | `effects/` | Make effects idempotent, then reconcile unknown outcomes. |
| 10 | `memory/` | Admit only reviewed, scoped, bounded prior knowledge. |
| 11 | `graph/spine.py` | Keep a long investigation on its active causal question. |
| 12–14 | `runtime/`, `integrations/` | Add owned work, dependency admission, and isolated analysis. |
| 15–17 | `decisions/`, `graph/`, `coordination/` | Route judgment, replace plans, and join specialist evidence. |
| 18–20 | `governance/` | Separate approval, authority, and policy. |
| 21 | `effects/enforcement.py` | Recheck policy at the exact effect boundary. |
| 22–24 | `evaluation/` | Trace trajectories, evaluate outcomes, and gate releases. |
| 25–28 | `operations/` | Observe safely, probe blind spots, learn boundaries, and enforce fleet limits. |
| 29–37 | `platform/` subdomains | Grow identity through executable launch risk one platform contract at a time. |

## Enforced rules

1. A package appears no earlier than its chapter.
2. Each README explains the pressure that caused its structural change.
3. README code maps name the real packages and execution path.
4. Generic buckets such as `helpers`, `utils`, and `misc` are forbidden.
5. Imports use responsibility packages rather than obsolete flat modules.
6. Demos and tests remain offline; retained live evidence keeps provenance.
7. Moving a module does not change its behavior in the same checkpoint.
8. Every adjacent chapter remains a clean cumulative diff.
9. `main` moves only after all behavioral and structural gates pass.

