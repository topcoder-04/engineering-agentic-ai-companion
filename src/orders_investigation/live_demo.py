"""Chapter 3 live-call records; normal execution remains offline."""

from dataclasses import asdict

from orders_investigation.domain.incident import Incident, opening_incident
from orders_investigation.environment.requests import OPENING_OBSERVATION_REQUESTS
from orders_investigation.decisions.model import DecisionReceipt
from orders_investigation.runtime.boundary import Request


def load_scenario(name: str) -> tuple[Incident, dict[str, Request]]:
    if name != "chapter-03":
        raise KeyError(name)
    return opening_incident(), dict(OPENING_OBSERVATION_REQUESTS)


def build_record(
    name: str,
    receipt: DecisionReceipt,
    incident: Incident,
    observations: dict[str, Request],
) -> dict:
    request = observations.get(receipt.choice.task_id)
    result = (
        {"kind": "boundary", "status": "refused", "reason": "unknown_observation"}
        if request is None
        else {
            "kind": "boundary",
            "status": "permitted",
            "request": asdict(request),
        }
    )
    return {
        "record_kind": "observed_live_model_call",
        "scenario": name,
        "source": receipt.source,
        "model": receipt.model,
        "observed_at": receipt.observed_at,
        "instructions": receipt.instructions,
        "input_text": receipt.input_text,
        "raw_output": receipt.raw_output,
        "response_id": receipt.response_id,
        "choice": asdict(receipt.choice),
        "deterministic_result": result,
    }


def build_failure_record(
    name: str,
    model: str,
    incident: Incident,
    observations: dict[str, Request],
    error: Exception,
    *,
    observed_at: str,
    elapsed_ms: int,
) -> dict:
    body = getattr(error, "body", {}) or {}
    return {
        "record_kind": "observed_live_model_failure",
        "scenario": name,
        "source": "openai",
        "model": model,
        "observed_at": observed_at,
        "instructions": None,
        "input_text": None,
        "raw_output": None,
        "response_id": getattr(error, "request_id", None),
        "elapsed_ms": elapsed_ms,
        "failure": {
            "type": type(error).__name__,
            "status_code": getattr(error, "status_code", None),
            "code": body.get("code"),
            "message": body.get("message", str(error)),
        },
        "choice": None,
        "deterministic_result": {"status": "not_evaluated"},
    }
