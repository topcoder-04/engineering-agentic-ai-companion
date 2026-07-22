"""Fail when retained evidence loses the provenance needed to interpret it."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
LIVE_FIELDS = {
    "record_kind", "scenario", "source", "model", "observed_at",
    "instructions", "input_text", "raw_output", "response_id",
    "deterministic_result",
}
ISOLATION_FIELDS = {
    "observed_at", "workflow_run_id", "workflow_job_id", "workflow_name",
    "runner_image", "base_commit", "head_commit", "outcomes", "claim_scope",
}


def validate(path: Path) -> None:
    payload = json.loads(path.read_text())
    required = ISOLATION_FIELDS if path.name == "docker-isolation.json" else LIVE_FIELDS
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError(f"{path.relative_to(ROOT)} missing provenance: {', '.join(missing)}")


def main() -> None:
    paths = sorted((ROOT / "evidence").glob("chapter-*/*.json"))
    if not paths:
        raise ValueError("no retained evidence found")
    for path in paths:
        validate(path)
    print(f"validated {len(paths)} evidence records")


if __name__ == "__main__":
    main()

