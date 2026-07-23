from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import re
from typing import Any


class EvidenceRefused(ValueError):
    pass


class DependencyUnavailable(RuntimeError):
    pass


class BreakerState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"


class EvidenceValueKind(StrEnum):
    IDENTIFIER = "identifier"
    RATIO = "ratio"


@dataclass(frozen=True)
class DependencyResult:
    source_system: str
    source_resource: str
    observed_at: datetime
    source_status: str
    fields: dict[str, Any]


@dataclass(frozen=True)
class EvidencePolicy:
    max_age: timedelta
    required_fields: tuple[str, ...]
    field_kinds: tuple[tuple[str, EvidenceValueKind], ...] = ()


@dataclass(frozen=True)
class EvidenceEnvelope:
    source_system: str
    source_resource: str
    observed_at: str
    admitted_at: str
    freshness_seconds: float
    completeness: str
    source_status: str
    fields: dict[str, Any]


def admit_evidence(
    result: DependencyResult,
    policy: EvidencePolicy,
    *,
    now: datetime,
) -> EvidenceEnvelope:
    if not result.source_system or not result.source_resource:
        raise EvidenceRefused("provenance_missing")
    if result.source_status != "ok":
        raise EvidenceRefused(f"source_status:{result.source_status}")

    age = now - result.observed_at
    if age < timedelta(0):
        raise EvidenceRefused("observation_time_in_future")
    if age > policy.max_age:
        raise EvidenceRefused("evidence_stale")

    missing = tuple(field for field in policy.required_fields if field not in result.fields)
    if missing:
        raise EvidenceRefused(f"evidence_partial:{','.join(missing)}")

    unexpected = tuple(sorted(set(result.fields) - set(policy.required_fields)))
    if unexpected:
        raise EvidenceRefused(f"evidence_unexpected_fields:{','.join(unexpected)}")

    for field, kind in policy.field_kinds:
        if field not in result.fields:
            continue
        value = result.fields[field]
        if kind == EvidenceValueKind.IDENTIFIER:
            valid = (
                isinstance(value, str)
                and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}", value) is not None
            )
        elif kind == EvidenceValueKind.RATIO:
            valid = (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and 0 <= value <= 1
            )
        else:
            valid = False
        if not valid:
            raise EvidenceRefused(f"evidence_value_invalid:{field}:{kind.value}")

    return EvidenceEnvelope(
        source_system=result.source_system,
        source_resource=result.source_resource,
        observed_at=result.observed_at.astimezone(timezone.utc).isoformat(),
        admitted_at=now.astimezone(timezone.utc).isoformat(),
        freshness_seconds=age.total_seconds(),
        completeness="complete",
        source_status=result.source_status,
        fields=result.fields,
    )


@dataclass
class CircuitBreaker:
    failure_threshold: int
    consecutive_failures: int = 0
    state: BreakerState = BreakerState.CLOSED

    def before_call(self) -> None:
        if self.state == BreakerState.OPEN:
            raise DependencyUnavailable("circuit_open")

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.state = BreakerState.CLOSED

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.state = BreakerState.OPEN


class HTTPXDependencyClient:
    """HTTP source adapter; evidence admission remains outside this client."""

    def __init__(self, base_url: str, breaker: CircuitBreaker, *, timeout_seconds: float):
        import httpx

        self.httpx = httpx
        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout_seconds,
            trust_env=False,
        )
        self.breaker = breaker

    def get_json(self, path: str) -> dict[str, Any]:
        self.breaker.before_call()
        try:
            response = self.client.get(path)
            response.raise_for_status()
        except self.httpx.HTTPError as exc:
            self.breaker.record_failure()
            raise DependencyUnavailable(type(exc).__name__) from exc
        self.breaker.record_success()
        return response.json()

