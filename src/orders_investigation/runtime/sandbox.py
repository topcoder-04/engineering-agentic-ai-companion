from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class ArtifactRefused(ValueError):
    pass


class ExecutionOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    NETWORK_DENIED = "network_denied"
    INPUT_DENIED = "input_denied"
    NONZERO_EXIT = "nonzero_exit"
    TIMEOUT = "timeout"
    OUTPUT_TOO_LARGE = "output_too_large"
    INVALID_ARTIFACT = "invalid_artifact"


@dataclass(frozen=True)
class GeneratedAnalysisRequest:
    analysis_id: str
    code_sha256: str
    input_sha256: str
    artifact_schema: str
    timeout_seconds: int
    max_output_bytes: int

    @property
    def digest(self) -> str:
        payload = json.dumps(self.__dict__, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class DiagnosticArtifact:
    analysis_id: str
    artifact_schema: str
    request_digest: str
    input_sha256: str
    image_digest: str
    findings: tuple[str, ...]


@dataclass(frozen=True)
class ExecutorResult:
    exit_code: int | None
    timed_out: bool = False
    network_denied: bool = False
    input_denied: bool = False
    artifact_bytes: bytes = b""


@dataclass(frozen=True)
class ArtifactDecision:
    outcome: ExecutionOutcome
    artifact: DiagnosticArtifact | None = None
    detail: str = ""


def make_request(code: bytes, input_bundle: bytes) -> GeneratedAnalysisRequest:
    return GeneratedAnalysisRequest(
        analysis_id="compare-writer-pressure",
        code_sha256=hashlib.sha256(code).hexdigest(),
        input_sha256=hashlib.sha256(input_bundle).hexdigest(),
        artifact_schema="diagnostic-artifact/v1",
        timeout_seconds=10,
        max_output_bytes=16_384,
    )


def docker_command(
    request: GeneratedAnalysisRequest,
    *,
    image_digest: str,
    input_directory: Path,
    output_directory: Path,
) -> tuple[str, ...]:
    if not image_digest.startswith("sha256:"):
        raise ValueError("image_digest_required")
    return (
        "docker", "run", "--rm",
        "--network", "none",
        "--read-only",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--memory", "256m",
        "--cpus", "0.5",
        "--mount", f"type=bind,src={input_directory},dst=/work/input,readonly",
        "--mount", f"type=bind,src={output_directory},dst=/work/output",
        image_digest,
        "python", "/work/request/analysis.py",
        "--input", "/work/input/evidence.json",
        "--output", "/work/output/artifact.json",
        "--analysis-id", request.analysis_id,
        "--artifact-schema", request.artifact_schema,
        "--request-digest", request.digest,
        "--input-sha256", request.input_sha256,
        "--image-digest", image_digest,
    )


def validate_artifact(
    raw: bytes,
    request: GeneratedAnalysisRequest,
    *,
    image_digest: str,
) -> DiagnosticArtifact:
    if len(raw) > request.max_output_bytes:
        raise ArtifactRefused("output_too_large")
    try:
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ArtifactRefused("invalid_json") from exc

    required = {
        "analysis_id", "artifact_schema", "request_digest",
        "input_sha256", "image_digest", "findings",
    }
    if set(data) != required:
        raise ArtifactRefused("artifact_shape_mismatch")
    if data["analysis_id"] != request.analysis_id:
        raise ArtifactRefused("analysis_id_mismatch")
    if data["artifact_schema"] != request.artifact_schema:
        raise ArtifactRefused("artifact_schema_mismatch")
    if data["request_digest"] != request.digest:
        raise ArtifactRefused("request_digest_mismatch")
    if data["input_sha256"] != request.input_sha256:
        raise ArtifactRefused("input_digest_mismatch")
    if data["image_digest"] != image_digest:
        raise ArtifactRefused("image_digest_mismatch")
    findings = data["findings"]
    if not isinstance(findings, list) or not findings or not all(
        isinstance(item, str) and item for item in findings
    ):
        raise ArtifactRefused("findings_invalid")
    return DiagnosticArtifact(
        analysis_id=data["analysis_id"],
        artifact_schema=data["artifact_schema"],
        request_digest=data["request_digest"],
        input_sha256=data["input_sha256"],
        image_digest=data["image_digest"],
        findings=tuple(findings),
    )


def admit_execution(
    result: ExecutorResult,
    request: GeneratedAnalysisRequest,
    *,
    image_digest: str,
) -> ArtifactDecision:
    if result.timed_out:
        return ArtifactDecision(ExecutionOutcome.TIMEOUT)
    if result.network_denied:
        return ArtifactDecision(ExecutionOutcome.NETWORK_DENIED)
    if result.input_denied:
        return ArtifactDecision(ExecutionOutcome.INPUT_DENIED)
    if result.exit_code != 0:
        return ArtifactDecision(ExecutionOutcome.NONZERO_EXIT, detail=str(result.exit_code))
    try:
        artifact = validate_artifact(result.artifact_bytes, request, image_digest=image_digest)
    except ArtifactRefused as exc:
        outcome = (
            ExecutionOutcome.OUTPUT_TOO_LARGE
            if str(exc) == "output_too_large"
            else ExecutionOutcome.INVALID_ARTIFACT
        )
        return ArtifactDecision(outcome, detail=str(exc))
    return ArtifactDecision(ExecutionOutcome.SUCCEEDED, artifact=artifact)
