from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class EvidenceKey(StrEnum):
    SERVICE_TIMEOUTS = "service_timeouts"
    DATABASE_WRITE_LATENCY = "database_write_latency"
    APPLICATION_CPU = "application_cpu"
    CONNECTION_POOL = "connection_pool"
    DATABASE_TOPOLOGY = "database_topology"
    WRITER_ACTIVITY = "writer_activity"
    REPLICATION_DELAY = "replication_delay"
    MIGRATION_JOB = "migration_job"
    PIPELINE_TRIGGER = "pipeline_trigger"


REQUIRED_EVIDENCE = frozenset({
    EvidenceKey.SERVICE_TIMEOUTS,
    EvidenceKey.WRITER_ACTIVITY,
    EvidenceKey.MIGRATION_JOB,
    EvidenceKey.PIPELINE_TRIGGER,
})


@dataclass(frozen=True)
class Evidence:
    key: EvidenceKey
    value: str
    source: str


@dataclass(frozen=True)
class HypothesisRevision:
    previous: str
    current: str
    based_on: tuple[EvidenceKey, ...]


@dataclass
class Incident:
    service: str = "orders-api"
    environment: str = "orders-production"
    hypothesis: str = "Pressure in the database path is delaying order completion."
    recorded_evidence: dict[EvidenceKey, Evidence] = field(default_factory=dict)
    hypothesis_revisions: list[HypothesisRevision] = field(default_factory=list)
    report_saved: bool = False

    @property
    def missing_evidence(self) -> tuple[EvidenceKey, ...]:
        return tuple(sorted(REQUIRED_EVIDENCE - self.recorded_evidence.keys()))

    @property
    def investigation_complete(self) -> bool:
        return not self.missing_evidence and self.report_saved

    def record_evidence(self, evidence: Evidence) -> None:
        self.recorded_evidence[evidence.key] = evidence

    def revise_hypothesis(
        self,
        current: str,
        *,
        based_on: tuple[EvidenceKey, ...],
    ) -> None:
        if not current.strip():
            raise ValueError("hypothesis_required")
        if not based_on:
            raise ValueError("supporting_evidence_required")
        missing = tuple(key for key in based_on if key not in self.recorded_evidence)
        if missing:
            raise ValueError(
                "supporting_evidence_not_recorded:"
                + ",".join(key.value for key in missing)
            )
        self.hypothesis_revisions.append(HypothesisRevision(
            previous=self.hypothesis,
            current=current,
            based_on=based_on,
        ))
        self.hypothesis = current


def opening_incident() -> Incident:
    incident = Incident()
    incident.record_evidence(Evidence(EvidenceKey.SERVICE_TIMEOUTS, "18%", "service_metrics"))
    incident.record_evidence(Evidence(EvidenceKey.DATABASE_WRITE_LATENCY, "4.8s", "database_monitoring"))
    incident.record_evidence(Evidence(EvidenceKey.APPLICATION_CPU, "within normal range", "service_metrics"))
    return incident

