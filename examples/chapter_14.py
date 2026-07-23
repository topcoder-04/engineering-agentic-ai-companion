"""Run one valid artifact and Chapter 14's six distinct refusal paths."""

import json

from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.sandbox import (
    ExecutorResult,
    admit_execution,
    make_request,
)


def main() -> None:
    demo = chapter_presentation(14, description=__doc__)

    image = "sha256:" + "a" * 64
    request = make_request(b"analysis code", b"evidence bundle")
    artifact = json.dumps(
        {
            "analysis_id": request.analysis_id,
            "artifact_schema": request.artifact_schema,
            "request_digest": request.digest,
            "input_sha256": request.input_sha256,
            "image_digest": image,
            "findings": ["Writer saturation begins after the migration starts."],
        }
    ).encode()
    accepted = admit_execution(
        ExecutorResult(0, artifact_bytes=artifact),
        request,
        image_digest=image,
    )
    refused_cases = (
        ("Network attempt", ExecutorResult(1, network_denied=True), "execution"),
        ("Outside input", ExecutorResult(1, input_denied=True), "execution"),
        ("Nonzero exit", ExecutorResult(7), "execution"),
        ("Timeout", ExecutorResult(None, timed_out=True), "execution"),
        (
            "Oversized output",
            ExecutorResult(0, artifact_bytes=b"x" * 16_385),
            "artifact admission",
        ),
        (
            "Invalid artifact",
            ExecutorResult(0, artifact_bytes=b'{"findings":[]}'),
            "artifact admission",
        ),
    )

    demo.scenario(1, "A successful executor result carries a valid artifact")
    demo.fields(
        (
            ("Analysis", request.analysis_id),
            ("Execution evidence", "deterministic fixture"),
            ("Request digest", request.digest[:16] + "…"),
            ("Input digest", request.input_sha256[:16] + "…"),
            ("Network", "denied"),
            ("Input mount", "read only"),
            ("Runtime limit", f"{request.timeout_seconds} seconds"),
            ("Output limit", f"{request.max_output_bytes:,} bytes"),
        ),
        style="evidence",
    )
    demo.decision(accepted.artifact is not None, approved_label="ARTIFACT ADMITTED")
    demo.execution(
        accepted.artifact is not None,
        "successful executor result observed",
    )
    if accepted.artifact is not None:
        demo.fields((("Finding", accepted.artifact.findings[0]),))

    demo.scenario(2, "Each failure remains distinct")
    for label, result, owner in refused_cases:
        decision = admit_execution(result, request, image_digest=image)
        detail = owner
        if decision.detail and decision.detail != decision.outcome.value:
            detail = f"{detail} · {decision.detail}"
        demo.result_row(
            label,
            accepted=False,
            outcome=decision.outcome.value,
            detail=detail,
        )

    demo.notice(
        "This deterministic demo proves request and admission behavior. "
        "scripts/chapter_14_isolation.py supplies the observed Docker "
        "enforcement evidence."
    )


if __name__ == "__main__":
    main()
