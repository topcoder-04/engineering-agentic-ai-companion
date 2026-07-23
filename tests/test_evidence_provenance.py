import json
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_every_retained_evidence_record_has_provenance():
    records = sorted((ROOT / "evidence").glob("chapter-*/*.json"))
    assert records
    live = {
        "record_kind", "scenario", "source", "model", "observed_at",
        "instructions", "input_text", "raw_output", "response_id",
        "deterministic_result",
    }
    isolation = {
        "observed_at", "workflow_run_id", "workflow_job_id", "workflow_name",
        "runner_image", "base_commit", "head_commit", "outcomes", "claim_scope",
    }
    for record in records:
        payload = json.loads(record.read_text())
        required = isolation if record.name == "docker-isolation.json" else live
        assert required <= payload.keys(), record
