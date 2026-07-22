# Mira's Journey — complete voice-over script

Target runtime: **9 minutes 14 seconds**  
Pace: calm and direct, around **140–150 words per minute**  
Playback: Chapter 1 holds for 15 seconds; Chapters 2–37 hold for 12 seconds; movement transitions hold for 18 seconds; the epilogue holds for 20 seconds; examples hold for 15 seconds.

The recording begins on Chapter 1. The setup screen remains available to readers, but it is not part of autoplay.

## 01 — Chapter 1: When a Good Answer Is Not the Work (00:00–00:15)

At 2:05 p.m., Orders starts timing out. Mira writes a useful update, but useful is not finished. The journey begins by separating evidence, hypothesis, and completed work.

## 02 — Chapter 2: What This Investigation May Touch (00:15–00:27)

The next clue may sit in metrics, database monitoring, jobs, or deployments. The investigation now names what it may touch and rejects everything else.

## 03 — Chapter 3: When Permitted Work Still Wastes Time (00:27–00:39)

Several checks are allowed, but only one is worth doing next. The model chooses among permitted work; deterministic code keeps control of execution.

## 04 — Chapter 4: When Evidence Changes the Shape of the Work (00:39–00:51)

Topology reveals that reads and writes follow different paths. Recorded evidence can add the next bounded task. Missing evidence cannot invent one.

## 05 — Chapter 5: What the Model Sees and What May Run (00:51–01:03)

The model sees one explicit decision surface. Its answer is only a proposal, and typed admission checks it against the system's current recorded state.

## 06 — Chapter 6: When Judgment Becomes a Dependency (01:03–01:15)

Every model turn costs time and money. Judgment gets a fixed budget and a fallback, so exploration stops deliberately instead of running forever.

## 07 — Chapter 7: Keeping Changed Work Alive After a Restart (01:15–01:27)

The process dies after three observations. Checkpointed state preserves the graph, evidence, and remaining budget, so the same investigation continues after restart.

## 08 — Controlled Work → Reliable Work (01:27–01:45)

The first layer is complete. Mira can now bound the investigation, let evidence shape the graph, admit proposals, limit judgment, and resume after failure. Next, that controlled work must survive retries, uncertainty, delegation, and hostile inputs.

## 09 — Chapter 8: Trying Again Without Doing It Twice (01:45–01:57)

The report service may already have accepted the write. A stable effect identity makes retry safe and prevents the same identity from hiding different work.

## 10 — Chapter 9: When an Attempt Ends but Its Effect Is Unknown (01:57–02:09)

A timeout does not prove failure. Unknown becomes a real outcome, and the system checks authoritative state before deciding whether to retry.

## 11 — Chapter 10: Carrying Forward Only What Helps (02:09–02:21)

Old incidents may help, but more context is not always better. Memory is filtered, bounded, and kept separate from evidence gathered in this run.

## 12 — Chapter 11: Keeping a Long Investigation on Course (02:21–02:33)

Reasonable next steps can still answer the wrong question. A task spine keeps the investigation's current mission in charge while preserving useful side findings.

## 13 — Chapter 12: Sharing Work Without Losing Ownership (02:33–02:45)

Two workers can see the same ready task. A time-limited claim and fencing token decide who owns it and block a stale worker from committing.

## 14 — Chapter 13: Depending on Systems That May Be Wrong (02:45–02:57)

Valid JSON can still contain instructions instead of facts. Dependency output becomes typed, sourced evidence; suspicious content is quarantined before it reaches judgment.

## 15 — Chapter 14: Running Generated Work Inside a Boundary (02:57–03:09)

Sometimes the model must generate a small analysis. It runs inside a fixed sandbox, and its result returns as untrusted data—not as authority.

## 16 — Reliable Work → Governed Effects (03:09–03:27)

The investigation now handles retries, unknown outcomes, memory, ownership, untrusted dependencies, and generated code without losing its shape. Reliability is necessary, but it does not answer who may approve a consequential effect or which policy governs it.

## 17 — Chapter 15: Choosing How Much Judgment a Decision Needs (03:27–03:39)

Not every decision needs the strongest model. Each choice declares the capability and data handling it requires, and the system selects a qualified option.

## 18 — Chapter 16: When New Evidence Changes What Comes Next (03:39–03:51)

New evidence can make a reasonable plan stale. Replanning replaces only future work, and late results from the old plan cannot take over.

## 19 — Chapter 17: When Useful Contributions Do Not Add Up (03:51–04:03)

Specialists can each be right without proving the whole case. Their assignments are explicit, and only compatible, complete results may be joined.

## 20 — Chapter 18: Waiting Safely for a Consequential Decision (04:03–04:15)

Human approval may arrive hours later. The exact intent is frozen first, so an expired answer or approval for different work is refused.

## 21 — Chapter 19: Knowing Who May Do What (04:15–04:27)

A valid session is not enough. The effect needs an exact grant for this action and resource; authority from a nearby system does not count.

## 22 — Chapter 20: Making Rules Independent of Wording (04:27–04:39)

Policy reads recorded facts, not persuasive language. Change a fact and the decision changes, with explicit obligations attached to every allowed action.

## 23 — Chapter 21: Enforcing Rules Where Effects Happen (04:39–04:51)

An earlier allow decision can become stale. The write boundary checks current facts again, applies every obligation, and records an enforcement receipt.

## 24 — Governed Effects → Judged Operations (04:51–05:09)

The effect path now carries model selection, replanning, joins, approval, authority, policy, and enforcement. The next question is operational: can we reconstruct the route, judge the full behavior, and stop a bad candidate from reaching production?

## 25 — Chapter 22: Seeing the Path, Not Only the Answer (05:09–05:21)

Logs alone cannot explain the result. A semantic trace connects evidence, decisions, joins, and effects while leaving sensitive content out.

## 26 — Chapter 23: Judging the Whole Trajectory (05:21–05:33)

A correct report can still come from a bad route. Evaluation now judges the full trajectory, with named cases, rubrics, versions, and visible disagreement.

## 27 — Chapter 24: Making Evaluation a Release Boundary (05:33–05:45)

A better average can hide a safety regression. Independent gates check safety and performance, and a failed evaluation blocks that exact candidate.

## 28 — Chapter 25: Observing Production Without Exposing It (05:45–05:57)

Green infrastructure can hide failed investigations. Redacted semantic events show where trajectories break without exposing the evidence that moved through them.

## 29 — Chapter 26: Testing What Authored Cases Missed (05:57–06:09)

Production finds combinations the authored suite missed. Variation testing changes one declared condition at a time, and important failures become permanent cases.

## 30 — Chapter 27: Turning Incidents Into Boundaries (06:09–06:21)

An incident is not closed by a restart. It becomes a missing invariant, a regression case, and an owned fix that must be proven.

## 31 — Chapter 28: Operating a Fleet Within Limits (06:21–06:33)

A healthy cell may still be the wrong cell. Routing checks location, authority, versions, capacity, and rollout stage before sending the run.

## 32 — Judged Operations → Operable Platform (06:33–06:51)

Mira can now trace, evaluate, release, observe, vary, learn from incidents, and route a fleet. But copied settings still drift between teams. The final layer turns those hard-won boundaries into platform contracts that every agent must satisfy.

## 33 — Chapter 29: Making an Agent Identifiable (06:51–07:03)

Approving an agent requires knowing exactly what it is. Prompt, tools, policy, and evaluations become one immutable runnable identity.

## 34 — Chapter 30: Admitting Capabilities, Not Copied Settings (07:03–07:15)

Teams declare the powers their agent needs. Central admission decides whether those capabilities are supported; a local settings edit cannot grant more.

## 35 — Chapter 31: Carrying the Caller's Authority (07:15–07:27)

The platform's service account is not the caller's permission. Delegated authority follows the request, and missing, expired, or wrong scope stops it.

## 36 — Chapter 32: Keeping Tenants and Data Inside Their Boundaries (07:27–07:39)

Tenant, data class, region, and retention rules determine where evidence may run and live. Cross-boundary sharing needs an explicit contract.

## 37 — Chapter 33: Making the Safe Path the Easy Path (07:39–07:51)

Safety loses when bypassing it is easier. A paved path supplies conforming defaults, keeps exceptions visible, and makes the approved route the fast route.

## 38 — Chapter 34: Binding Proof to the Release (07:51–08:03)

Evaluation proof must match what ships. The conformance receipt binds evidence to the exact artifact digest, so candidate A cannot release candidate B.

## 39 — Chapter 35: Owning the Agent After Launch (08:03–08:15)

Launch is not the end of ownership. A named operator, runbook, rollback path, and budget owner stay attached to the running agent.

## 40 — Chapter 36: Evolving the Platform Without Breaking Every Team (08:15–08:27)

Shared contracts will change at different speeds. Compatibility windows keep supported versions working and block migrations that would break existing readers.

## 41 — Chapter 37: Making Risk Posture an Engineering Contract (08:27–08:39)

Risk becomes executable evidence, not a review note. Consequential work cannot launch until evaluation, ownership, rollback, caller authority, and placement are proven.

## 42 — Epilogue: The Work Can Now Outlive the Builder (08:39–08:59)

Six months later, a new on-call engineer opens the run without Mira beside them. The evidence, task graph, decisions, model calls, report intent, receipts, and ownership are still there. The system can explain itself because its boundaries live in the work, not in one person's memory.

## 43 — Examples: Run the System (08:59–09:14)

The journey is meant to be used. Run the Orders investigation, open any chapter branch to study one boundary, or change one condition and watch the system refuse unsafe work. That is where the diagram becomes engineering practice.
