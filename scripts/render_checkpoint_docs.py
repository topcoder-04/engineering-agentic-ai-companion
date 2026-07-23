"""Render branch-local README and architecture contracts.

Run this after checking out a ``chapter-NN`` checkpoint. The implementation
tree remains the source of truth for what exists; the chapter metadata explains
why each responsibility was earned.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).parents[1]

EXPECTED = {
    1: "The report update succeeds, but missing evidence keeps completion false.",
    2: "Orders observations are permitted; another environment, rollback, and an unknown operation are refused before outside work.",
    3: "The permitted connection-pool check closes no evidence gap; topology becomes the next useful choice.",
    4: "Topology creates writer and replica work; writer and migration evidence create the pipeline task.",
    5: "The pipeline proposal is admitted, while its unsupported parallelism reason remains outside evidence.",
    6: "Two timed-out attempts consume 8,000 ms, return no choice, and stop with model_timeout.",
    7: "The changed graph, recorded evidence, and one charged model attempt survive restoration.",
    8: "The first response is lost after commit; the exact retry replays one stored effect.",
    9: "A post-dispatch timeout remains unknown until reconciliation finds the succeeded effect.",
    10: "Five hundred eligible records are reduced to the ranked three-record prefix, with 497 omissions visible.",
    11: "The boundary and graph allow the replication check; only the active task spine refuses the drift.",
    12: "Worker B takes over with token 2; worker A's late token-1 commit is refused.",
    13: "Current complete evidence is admitted; stale, partial, and instruction-bearing results are refused distinctly.",
    14: "One artifact is validated and six failures remain distinct: timeout, network, input, exit, size, and shape.",
    15: "Task choice, standard analysis, restricted analysis, and no-eligible-source cases select only requirement-compatible sources.",
    16: "Succeeded work survives, obsolete future work is superseded, and the old plan version cannot commit.",
    17: "One specialist return remains incomplete; two exact compatible returns create a proposal but no outside effect.",
    18: "A changed-intent signal is refused; the exact correlated signal approves the durable request.",
    19: "The verified session and exact grant authorize one effect; a changed operation is refused.",
    20: "Different request wording produces the same structured decision; stale evidence changes the decision to deny.",
    21: "The exact effect receipt advances report version 7 to 8; bypass, stale policy, and stale facts leave version 7 unchanged.",
    22: "The two-event trace reports no integrity reasons and a 25 ms recorded duration without raw content.",
    23: "The complete path passes every dimension; the refused path reports its failed dimensions and reasons.",
    24: "Empty evaluation evidence fails closed, a safe campaign passes, and a forbidden action triggers the safety veto.",
    25: "The operational view keeps component, two evidence references, and 20 model units without raw evidence.",
    26: "The two-by-two-by-two matrix executes eight stable variations and exposes the first refusal.",
    27: "The promoted regression has a named owner and deterministic failure signature; only the corrected path passes.",
    28: "Eligibility selects the healthy ready cell before optimization; a failed release cannot be routed.",
    29: "The exact registered version resolves to its owner and stable manifest digest; an unknown version is refused.",
    30: "The matching capability profile is admitted; an incompatible profile is refused before work.",
    31: "The delegated report action runs; refund.issue is refused for the same caller and agent.",
    32: "The exact European target is selected; a US residency request is refused instead of taking a least-wrong target.",
    33: "The paved path generates agent.yaml, its conformance test, and runbook.md with no exceptions.",
    34: "Evidence bound to candidate A passes; the same receipt presented for candidate B is refused.",
    35: "The owned candidate runs, while a non-waivable residency exception remains refused.",
    36: "The first migration decision is advance_readers_first; an incompatible reader holds execution.",
    37: "Complete launch evidence passes; six separate candidates each remove one required proof, produce exactly one launch veto, and show NOT EXECUTED.",
}

EVOLUTION = {
    1: ("`domain/`, `environment/`, `presentation/`", "Separate completion facts from outside observations and effects, then render their proof consistently."),
    2: ("`runtime/boundary.py`", "Declare what the investigation may observe or change."),
    3: ("`decisions/model.py`", "Keep probabilistic choice behind a provider-neutral seam."),
    4: ("`graph/tasks.py`", "Let recorded evidence create concrete dependent work."),
    5: ("`context/`, `runtime/contracts/`", "Separate the model-visible surface, proposal admission, and execution."),
    6: ("`decisions/budget.py`", "Make variable judgment a bounded dependency."),
    7: ("`runtime/workflow.py`", "Persist changed work and charged attempts across restart."),
    8: ("`effects/idempotency.py`", "Give a consequential effect stable identity."),
    9: ("`effects/reconciliation.py`", "Preserve unknown outcomes until effect truth is recovered."),
    10: ("`memory/`", "Admit only reviewed, scoped, bounded prior knowledge."),
    11: ("`graph/spine.py`", "Constrain ready work to the active causal question."),
    12: ("`runtime/ownership.py`", "Lease work while fencing stale completion."),
    13: ("`integrations/`", "Admit typed dependency results at the source boundary."),
    14: ("`runtime/sandbox.py`", "Run generated analysis inside an isolated, artifact-checked boundary."),
    15: ("`decisions/routing.py`", "Match judgment consequence to a compatible source."),
    16: ("`graph/planning.py`", "Replace future commitments without rewriting succeeded history."),
    17: ("`coordination/`", "Join exact delegated returns under one owner."),
    18: ("`governance/approval.py`", "Persist and correlate consequential approval."),
    19: ("`governance/authority.py`", "Bind verified identity to one exact delegated grant."),
    20: ("`governance/policy.py`", "Decide from structured facts rather than wording."),
    21: ("`effects/enforcement.py`, `runtime/journey.py`", "Recheck policy at the effect and compose the cumulative Orders path."),
    22: ("`evaluation/`", "Preserve the semantic trajectory needed for judgment."),
    23: ("`evaluation/production.py`", "Evaluate outcomes and path dimensions together."),
    24: ("`evaluation/production.py` release gate", "Turn evaluation evidence into a fail-closed release decision."),
    25: ("`operations/observability.py`", "Expose useful production fields without raw content."),
    26: ("`operations/probes.py`", "Exercise deliberate model, dependency, and timing variations."),
    27: ("`operations/learning.py`", "Promote incident failures into owned regression boundaries."),
    28: ("`operations/fleet.py`", "Route released candidates within shared cell limits."),
    29: ("`platform/identity/`", "Resolve every agent version to an immutable contract."),
    30: ("`platform/capabilities/`", "Admit compatible capabilities instead of copying settings."),
    31: ("`platform/authority/`", "Carry caller authority without becoming a confused deputy."),
    32: ("`platform/placement/`", "Make tenant, residency, data class, and retention structural."),
    33: ("`platform/defaults/`", "Make the safe platform path the easiest path."),
    34: ("`platform/releases/`", "Bind conformance evidence to the exact candidate artifact."),
    35: ("`platform/lifecycle/`", "Keep ownership and exceptions operable after launch."),
    36: ("`platform/compatibility/`", "Advance readers before writers depend on a new contract."),
    37: ("`platform/risk/`", "Preserve independent launch vetoes as an executable posture."),
}

PACKAGE_ORDER = (
    "domain",
    "environment",
    "presentation",
    "runtime",
    "decisions",
    "graph",
    "context",
    "effects",
    "memory",
    "integrations",
    "coordination",
    "governance",
    "evaluation",
    "operations",
    "platform",
)
PLATFORM_ORDER = (
    "identity",
    "capabilities",
    "authority",
    "placement",
    "defaults",
    "releases",
    "lifecycle",
    "compatibility",
    "risk",
)


def present_packages() -> tuple[list[str], list[str]]:
    source = ROOT / "src" / "orders_investigation"
    packages = [
        name for name in PACKAGE_ORDER if (source / name / "__init__.py").exists()
    ]
    platform = source / "platform"
    subdomains = [
        name
        for name in PLATFORM_ORDER
        if (platform / name / "__init__.py").exists()
    ]
    return packages, subdomains


def architecture_tree() -> str:
    packages, subdomains = present_packages()
    source = ROOT / "src" / "orders_investigation"
    root_files = [
        name
        for name in ("demo.py", "live_demo.py")
        if (source / name).exists()
    ]
    entries = [("package", name) for name in packages] + [
        ("file", name) for name in root_files
    ]
    lines = ["src/orders_investigation/"]
    for index, (kind, name) in enumerate(entries):
        last = index == len(entries) - 1
        branch = "└──" if last else "├──"
        suffix = "/" if kind == "package" else ""
        lines.append(f"{branch} {name}{suffix}")
        package = name
        if kind == "package" and package == "platform":
            prefix = "    " if last else "│   "
            for sub_index, subdomain in enumerate(subdomains):
                sub_branch = "└──" if sub_index == len(subdomains) - 1 else "├──"
                lines.append(f"{prefix}{sub_branch} {subdomain}/")
    return "\n".join(lines)


def render_architecture(chapter: int) -> str:
    rows = [
        f"| {number} | {EVOLUTION[number][0]} | {EVOLUTION[number][1]} |"
        for number in range(1, chapter + 1)
    ]
    checkpoint_scope = (
        "The complete architecture earned across all 37 chapters is now present. "
        "Earlier `chapter-NN` branches retain only the responsibilities earned by "
        "that checkpoint."
        if chapter == 37
        else (
            f"Responsibilities introduced after Chapter {chapter} are intentionally "
            "absent from this checkpoint. `main` is the complete Chapter 37 map."
        )
    )
    return "\n".join(
        [
            "# Architecture evolution contract",
            "",
            f"**Current checkpoint: Chapter {chapter}.** This document describes what is present now. It does not advertise packages from later checkpoints.",
            "",
            "## Present responsibility map",
            "",
            "```text",
            architecture_tree(),
            "```",
            "",
            "## Evolution earned so far",
            "",
            "| Chapter | Boundary introduced | Why it appears here |",
            "|---:|---|---|",
            *rows,
            "",
            checkpoint_scope,
            "",
            "## Enforced rules",
            "",
            "1. A package appears no earlier than the chapter that earns it.",
            "2. The README names the pressure, executable path, focused test, and expected outcome.",
            "3. Code maps name real tracked paths; empty future packages are forbidden.",
            "4. Generic buckets such as `helpers`, `utils`, and `misc` are forbidden.",
            "5. Demos and tests are deterministic and offline; retained live evidence keeps provenance.",
            "6. Adjacent chapter branches remain clean cumulative prefixes.",
            "7. `main` moves only after all branch-local behavioral and structural gates pass.",
            "",
        ]
    )


def run_section(chapter: int) -> str:
    replay = ""
    if chapter == 7:
        replay = (
            "\nThe Part 1 interlude replay is also executable:\n\n"
            "```bash\npython -m orders_investigation.demo foundation-replay\n```\n"
        )
    elif chapter == 14:
        replay = (
            "\nThe Part 2 interlude and optional Docker probe are also executable:\n\n"
            "```bash\n"
            "python -m orders_investigation.demo part-2-replay\n"
            "python scripts/chapter_14_isolation.py\n"
            "```\n"
        )
    return f"""## Run this checkpoint

Prerequisites are Python 3.11 or newer and Git. Docker is optional and used only by the Chapter 14 host-isolation probe; OPA is optional for the Chapter 20 Rego mapping.

Use the portable reader path from a fresh checkout:

```bash
git switch chapter-{chapter:02d}
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest tests/test_chapter_{chapter:02d}.py
python -m pytest
python scripts/run_current_chapter.py
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`. The manuscript-compatible command executes the same chapter file:

```bash
python -m orders_investigation.demo chapter-{chapter:02d}
```
{replay}
Expected outcome: {EXPECTED[chapter]}

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
uv run --no-sync pytest tests/test_chapter_{chapter:02d}.py
uv run --no-sync pytest
uv run --no-sync python scripts/run_current_chapter.py
```

The `test` extra is the portable reader contract. CI installs the all-extras superset, so optional LangGraph and HTTPX integration coverage may add checks without changing the chapter's offline acceptance result.
"""


def complete_shared_code_map(readme: str) -> str:
    match = re.search(
        r"(## (?:Code|Repository) map\s*\n+```text\n)(.*?)(\n```)",
        readme,
        re.DOTALL,
    )
    if match is None:
        raise ValueError("README code map not found")
    body = match.group(2)
    shared_paths = (
        "src/orders_investigation/presentation/__init__.py",
        "src/orders_investigation/presentation/chapters.py",
        "src/orders_investigation/presentation/terminal.py",
        "tests/test_demo_presentation.py",
        "scripts/run_current_chapter.py",
    )
    existing = set(body.splitlines())
    missing = [path for path in shared_paths if path not in existing]
    if missing:
        body = body.rstrip() + "\n" + "\n".join(missing)
    return readme[: match.start(2)] + body + readme[match.end(2) :]


def chapter_37_base_readme() -> str:
    return """# Chapter 37 companion — Making Risk Posture an Engineering Contract

Chapter 36 made platform evolution compatible. This final checkpoint makes the
launch posture executable: the candidate may run only when the proof chain
matches its consequence and every hard obligation remains satisfied.

## What this chapter adds

- Consequence-selected risk tiers and independent hard launch vetoes live in
  `platform/risk/`.
- Launch evidence is derived from executed variations, lifecycle ownership,
  artifact-bound conformance, caller authorization, and data-safe placement.
- The complete demo follows one accepted candidate through the assembled system,
  then removes one proof at a time and shows six exact refusals.

## Code map

```text
src/orders_investigation/platform/risk/__init__.py
src/orders_investigation/runtime/journey.py
src/orders_investigation/presentation/__init__.py
src/orders_investigation/presentation/chapters.py
src/orders_investigation/presentation/terminal.py
examples/chapter_37.py
tests/test_chapter_37.py
tests/test_demo_presentation.py
scripts/run_current_chapter.py
scripts/validate_evidence.py
```

The map names the Chapter 37 delta and the shared surfaces that make its
behavior visible. Every earlier responsibility remains executable through the
cumulative suite.
"""


def render_readme(chapter: int) -> str:
    existing = (ROOT / "README.md").read_text()
    if chapter == 37 and existing.startswith(
        "# Engineering Agentic AI — executable companion"
    ):
        existing = chapter_37_base_readme()
    readme = complete_shared_code_map(existing)
    run_pattern = re.compile(
        r"\n## Run this checkpoint\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )
    replacement = "\n" + run_section(chapter).rstrip() + "\n"
    if run_pattern.search(readme):
        readme = run_pattern.sub(lambda _: replacement, readme, count=1)
    else:
        readme += replacement

    architecture = (
        "\n## Architecture evolution at this checkpoint\n\n"
        "The tracked responsibility map now contains only the packages earned through "
        f"Chapter {chapter}. Later packages are absent from this branch.\n\n"
        "```text\n"
        f"{architecture_tree()}\n"
        "```\n\n"
        f"`ARCHITECTURE.md` records only Chapters 1-{chapter} as present evolution; "
        "`main` carries the complete roadmap.\n"
    )
    architecture_pattern = re.compile(
        r"\n## Architecture evolution(?: at this checkpoint)?\n.*\Z",
        re.DOTALL,
    )
    if architecture_pattern.search(readme):
        readme = architecture_pattern.sub(lambda _: architecture, readme, count=1)
    else:
        readme = readme.rstrip() + "\n" + architecture
    return readme.rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("chapter", type=int, choices=range(1, 38))
    arguments = parser.parse_args()
    (ROOT / "README.md").write_text(render_readme(arguments.chapter))
    (ROOT / "ARCHITECTURE.md").write_text(render_architecture(arguments.chapter))


if __name__ == "__main__":
    main()
