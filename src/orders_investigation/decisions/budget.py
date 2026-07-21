from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Callable

from orders_investigation.decisions.model import ModelChoice


class AttemptOutcome(StrEnum):
    CHOICE = "choice"
    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ModelAttempt:
    outcome: AttemptOutcome
    elapsed_ms: int
    choice: ModelChoice | None = None
    input_units: int | None = None
    output_units: int | None = None


@dataclass(frozen=True)
class DecisionBudget:
    max_calls: int = 6
    per_call_timeout_ms: int = 4_000
    max_input_units: int = 20_000
    max_output_units: int = 4_000
    max_retries: int = 1


@dataclass
class DecisionLedger:
    budget: DecisionBudget
    attempts: list[ModelAttempt] = field(default_factory=list)

    @property
    def total_input_units(self) -> int:
        return sum(item.input_units or 0 for item in self.attempts)

    @property
    def total_output_units(self) -> int:
        return sum(item.output_units or 0 for item in self.attempts)

    @property
    def total_elapsed_ms(self) -> int:
        return sum(item.elapsed_ms for item in self.attempts)

    def may_start_call(self) -> bool:
        return (
            len(self.attempts) < self.budget.max_calls
            and self.total_input_units < self.budget.max_input_units
            and self.total_output_units < self.budget.max_output_units
        )

    def record(self, attempt: ModelAttempt) -> None:
        if attempt.outcome == AttemptOutcome.CHOICE and attempt.choice is None:
            raise ValueError("choice_outcome_requires_choice")
        if attempt.outcome != AttemptOutcome.CHOICE and attempt.choice is not None:
            raise ValueError("failed_attempt_cannot_contain_choice")
        self.attempts.append(attempt)

    def to_data(self) -> dict[str, object]:
        return {
            "budget": asdict(self.budget),
            "attempts": [
                {
                    "outcome": attempt.outcome.value,
                    "elapsed_ms": attempt.elapsed_ms,
                    "choice": asdict(attempt.choice) if attempt.choice else None,
                    "input_units": attempt.input_units,
                    "output_units": attempt.output_units,
                }
                for attempt in self.attempts
            ],
        }

    @classmethod
    def from_data(cls, data: dict[str, object]) -> "DecisionLedger":
        ledger = cls(DecisionBudget(**data["budget"]))
        for row in data["attempts"]:
            choice = ModelChoice(**row["choice"]) if row["choice"] else None
            ledger.record(ModelAttempt(
                outcome=AttemptOutcome(row["outcome"]),
                elapsed_ms=row["elapsed_ms"],
                choice=choice,
                input_units=row["input_units"],
                output_units=row["output_units"],
            ))
        return ledger


@dataclass(frozen=True)
class DecisionRun:
    choice: ModelChoice | None
    stop_reason: str | None


def obtain_choice(
    call: Callable[[int], ModelAttempt],
    ledger: DecisionLedger,
) -> DecisionRun:
    retries = 0
    while True:
        if not ledger.may_start_call():
            return DecisionRun(None, "decision_budget_exhausted")
        attempt = call(ledger.budget.per_call_timeout_ms)
        ledger.record(attempt)
        if attempt.outcome == AttemptOutcome.CHOICE:
            return DecisionRun(attempt.choice, None)
        if retries >= ledger.budget.max_retries:
            return DecisionRun(None, f"model_{attempt.outcome.value}")
        retries += 1
