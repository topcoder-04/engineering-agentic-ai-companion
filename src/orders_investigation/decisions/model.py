from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from orders_investigation.runtime.contracts.admission import Proposal


@dataclass(frozen=True)
class ModelChoice:
    task_id: str
    reason: str
    expected_evidence: str


@dataclass(frozen=True)
class DecisionReceipt:
    choice: ModelChoice
    source: str
    model: str
    elapsed_ms: int | None
    input_units: int | None = None
    output_units: int | None = None
    observed_at: str | None = None
    instructions: str | None = None
    input_text: str | None = None
    raw_output: str | None = None
    response_id: str | None = None


CHOICE_INSTRUCTIONS = """You choose one next observation for an incident investigation.

Use only a task_id listed in ready_tasks.
Do not claim that a task is permitted merely because it appears in the input.
Give a concise reason grounded only in recorded_evidence, and name the evidence you
expect the observation to return.
Return exactly task_id, reason, and expected_evidence.
Do not issue commands. Do not describe an action as completed."""


@dataclass(frozen=True)
class ModelRequest:
    instructions: str
    input_text: str


def build_model_request(decision_surface: str) -> ModelRequest:
    return ModelRequest(CHOICE_INSTRUCTIONS, decision_surface)


class ChoiceModel(Protocol):
    def choose(self, prompt: str) -> DecisionReceipt: ...


class FixedChoiceModel:
    def __init__(self, choice: ModelChoice):
        self.choice = choice

    def choose(self, prompt: str) -> DecisionReceipt:
        request = build_model_request(prompt)
        return DecisionReceipt(
            self.choice,
            "fixed",
            "fixed-choice",
            None,
            instructions=request.instructions,
            input_text=request.input_text,
            raw_output=json.dumps(self.choice.__dict__, sort_keys=True),
        )


class OpenAIChoiceModel:
    """Optional live adapter using the same proposal schema as admission."""

    def __init__(self, model: str | None = None):
        from openai import OpenAI

        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = model or os.environ["ORDERS_MODEL"]

    def choose(self, prompt: str) -> DecisionReceipt:
        request = build_model_request(prompt)
        started = time.perf_counter()
        observed_at = datetime.now(timezone.utc).isoformat()
        response = self.client.responses.parse(
            model=self.model,
            instructions=request.instructions,
            input=request.input_text,
            text_format=Proposal,
        )
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        raw_output = response.output_text
        proposal = response.output_parsed
        if proposal is None:
            raise ValueError("model_choice_missing")
        choice = ModelChoice(**proposal.model_dump())
        usage = getattr(response, "usage", None)
        return DecisionReceipt(
            choice,
            "openai",
            self.model,
            elapsed_ms,
            input_units=getattr(usage, "input_tokens", None),
            output_units=getattr(usage, "output_tokens", None),
            observed_at=observed_at,
            instructions=request.instructions,
            input_text=request.input_text,
            raw_output=raw_output,
            response_id=getattr(response, "id", None),
        )

