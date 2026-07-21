from dataclasses import dataclass
from enum import StrEnum


class EvidenceKey(StrEnum):
    SERVICE_TIMEOUTS = "service_timeouts"
    DATABASE_WRITE_LATENCY = "database_write_latency"
    APPLICATION_CPU = "application_cpu"
    WRITER_ACTIVITY = "writer_activity"
    MIGRATION_JOB = "migration_job"
    PIPELINE_TRIGGER = "pipeline_trigger"


@dataclass(frozen=True)
class Evidence:
    """A fact recorded from an incident source, not generated language."""

    key: EvidenceKey
    value: str
    source: str
