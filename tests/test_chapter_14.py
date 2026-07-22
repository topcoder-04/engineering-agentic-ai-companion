import json

from orders_investigation.runtime.sandbox import (
    ExecutionOutcome,
    ExecutorResult,
    admit_execution,
    make_request,
)


IMAGE = "sha256:" + "a" * 64


def valid_artifact(request):
    return json.dumps({
        "analysis_id": request.analysis_id,
        "artifact_schema": request.artifact_schema,
        "request_digest": request.digest,
        "input_sha256": request.input_sha256,
        "image_digest": IMAGE,
        "findings": ["Writer saturation begins after the migration starts."],
    }).encode()


def test_valid_artifact_is_admitted_with_request_and_input_identity():
    request = make_request(b"analysis code", b"evidence bundle")
    decision = admit_execution(
        ExecutorResult(exit_code=0, artifact_bytes=valid_artifact(request)),
        request,
        image_digest=IMAGE,
    )
    assert decision.outcome == ExecutionOutcome.SUCCEEDED
    assert decision.artifact.input_sha256 == request.input_sha256


def test_execution_failures_remain_distinct():
    request = make_request(b"analysis code", b"evidence bundle")
    cases = (
        (ExecutorResult(exit_code=None, timed_out=True), ExecutionOutcome.TIMEOUT),
        (ExecutorResult(exit_code=1, network_denied=True), ExecutionOutcome.NETWORK_DENIED),
        (ExecutorResult(exit_code=1, input_denied=True), ExecutionOutcome.INPUT_DENIED),
        (ExecutorResult(exit_code=7), ExecutionOutcome.NONZERO_EXIT),
    )
    for result, expected in cases:
        assert admit_execution(result, request, image_digest=IMAGE).outcome == expected


def test_oversized_and_invalid_artifacts_are_refused_after_execution():
    request = make_request(b"analysis code", b"evidence bundle")
    oversized = ExecutorResult(exit_code=0, artifact_bytes=b"x" * 16_385)
    invalid = ExecutorResult(exit_code=0, artifact_bytes=b'{"findings": []}')
    assert admit_execution(oversized, request, image_digest=IMAGE).outcome == ExecutionOutcome.OUTPUT_TOO_LARGE
    decision = admit_execution(invalid, request, image_digest=IMAGE)
    assert decision.outcome == ExecutionOutcome.INVALID_ARTIFACT
    assert decision.detail == "artifact_shape_mismatch"
