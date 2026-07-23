# Mira's Journey — narrative voice-over

Video runtime: **7 minutes 16.500 seconds**  
Spoken narration: approximately **6 minutes 45 seconds**  
Delivery: warm, direct, and unhurried at **118–125 words per minute**

Render the video from `miras-journey.html?video=1` at **1920 × 1080,
30 frames per second**. Capture mode holds the opening frame for 1 second,
then follows the same chapter, waypoint, epilogue, and examples timing used
below. Stop the export at exactly **00:07:16.500**; the examples frame remains
visible during the closing silence.

The screen already names every chapter. Do not read those labels aloud. The
voice-over has a different job: follow Mira through one Orders incident, explain
why each layer becomes necessary, and leave the listener wanting to examine the
book and runnable companion.

Begin each cue about half a second after its visual range starts. The unused time
is intentional. Let the building grow in silence; do not rush to fill every
frame.

**00:00.000–00:01.000 — silence.** The empty ground appears.

## 01 — The incident (00:01.000–00:37.500)

At 2:05 p.m., Orders begins timing out. Mira has enough evidence to sound
convincing: application CPU looks normal, while database writes are suddenly
slow. A model can turn that into a polished explanation in seconds. But a
polished explanation does not finish the investigation. Mira still needs to
know what is missing, what actually ran, and whether the report was updated.
This book begins in that gap.

## 02 — From an answer to controlled work (00:37.500–01:00.000)

Mira draws a boundary around what the investigation may touch. The model chooses
among ready options, but code decides what is admitted and executed. New
evidence can change the task graph. The model cannot invent work simply because
it sounds useful.

## 03 — A workflow that can stop and continue (01:00.000–01:23.000)

Judgment also needs limits. Mira gives it a budget and a fallback, then
checkpoints the graph, evidence, and remaining work. A crash no longer erases
the investigation. By the end of this first layer, a useful answer has become a
controlled workflow.

## 04 — Controlled work is not yet reliable (01:23.000–01:41.500)

One idea now holds the system together: the model may be flexible because the
boundary is not. But production is messy. Requests repeat, replies disappear,
workers overlap, and dependencies cannot always be trusted.

## 05 — Surviving retries and uncertainty (01:41.500–02:12.000)

After a restart, Mira sees a report update that may already have succeeded. A
stable effect identity makes retry safe. When a reply is lost, the outcome is
recorded as unknown—not guessed to be a failure. The system reconciles with the
authoritative source before deciding what to do next. Reliability starts by
being honest about uncertainty.

## 06 — Keeping the investigation intact (02:12.000–02:43.500)

Old incidents can help, but only as bounded memory, never as fresh evidence. A
task spine keeps the original question in charge. Claims prevent two workers
from owning the same result. Dependency output is treated as untrusted evidence,
and generated analysis runs inside a sandbox. The investigation can now survive
the ordinary failures of production without losing its shape.

## 07 — Reliable work is not automatically allowed work (02:43.500–03:02.500)

Mira has made the workflow reliable. That still does not answer the harder
questions: who may approve an effect, whose authority is being used, and which
policy must hold when the write actually happens?

## 08 — Judgment changes as evidence changes (03:02.500–03:30.500)

Not every choice needs the strongest model. Mira matches the model to the
decision and the data it must handle. Plans name the evidence behind them, so
new facts can replace only future work. Specialists may contribute pieces, but
their results count only when they fit together and support the same claim.

## 09 — Governance reaches the effect (03:30.500–04:05.500)

Consequential work can wait for a person, but the exact intent is frozen before
approval. Authority is checked for this caller, this action, and this resource.
Policy reads facts instead of persuasive wording. Then, at the report write,
current facts are checked again, obligations are applied, and a receipt is
recorded. Governance is no longer advice around the workflow. It is part of the
effect path.

## 10 — A governed result can still hide a bad journey (04:05.500–04:22.000)

Orders can now produce a governed effect. But a correct-looking report may
still come from an unsafe path. The next layer judges the journey, not just the
final sentence.

## 11 — Judging the route, not only the answer (04:22.000–04:48.000)

A semantic trace connects evidence, decisions, joins, and effects without
exposing their contents. Evaluation can now judge the complete trajectory.
Safety and performance gate separately, so a better average cannot hide a
serious regression. A candidate reaches release only after it proves the
boundaries it claims to preserve.

## 12 — Turning production failures into new boundaries (04:48.000–05:15.500)

In production, redacted events show where investigations abandon or refuse.
Variation tests explore combinations the authored cases missed. When an
incident still occurs, it becomes a missing invariant, a regression case, and
an owned fix. Fleet routing then places work only where location, authority,
version, capacity, and rollout rules all agree.

## 13 — One safe agent is not an operable platform (05:15.500–05:33.500)

Mira's problem has changed. She is no longer protecting one Orders
investigation. She needs the same hard-won boundaries to hold across teams,
agents, and releases—without every team rebuilding them differently.

## 14 — The platform must know what is running (05:33.500–06:00.000)

The platform starts with identity: one exact combination of prompt, tools,
policy, and evaluations. Capabilities are declared and centrally admitted.
Every run carries the caller's authority instead of borrowing a powerful
platform account. Tenant, region, data class, and retention rules decide where
the evidence may run and live.

## 15 — Launch must be earned (06:00.000–06:37.000)

The safe path becomes the easy path, but convenience is not proof. A
conformance receipt binds evaluation to the artifact being released. A named
operator, runbook, rollback path, and budget owner remain attached after launch.
Compatibility rules let the platform evolve without breaking every team.
Finally, risk becomes executable evidence. A consequential agent launches only
when its evaluation, ownership, rollback, caller authority, and placement match
the harm it could cause.

## 16 — The work outlives Mira (06:37.000–06:58.000)

Six months later, a new on-call engineer opens the Orders investigation. They
never met Mira, but its evidence, decisions, approvals, receipts, and ownership
are still connected. The work outlives its builder because the reasoning lives
in the system.

## 17 — Invitation (06:58.000–07:13.500)

This is not an architecture poster. Every boundary runs both ways: success and
refusal. The book shows how an agent earns trust, one boundary at a time.

**07:13.500–07:16.500 — silence.** Hold on the runnable examples.
