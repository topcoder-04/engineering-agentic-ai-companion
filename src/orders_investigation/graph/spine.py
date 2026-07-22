from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass


class SpineTransitionRefused(ValueError):
    pass


@dataclass(frozen=True)
class SpineMilestone:
    milestone_id: str
    question: str
    allowed_tasks: tuple[str, ...]


MILESTONES = {
    "locate_pressure": SpineMilestone(
        "locate_pressure",
        "Where is order-completion pressure accumulating?",
        ("inspect_database_topology", "inspect_writer_activity"),
    ),
    "identify_workload": SpineMilestone(
        "identify_workload",
        "Which workload is consuming writer capacity?",
        ("inspect_migration_job",),
    ),
    "identify_trigger": SpineMilestone(
        "identify_trigger",
        "What introduced the migration workload?",
        ("inspect_pipeline_run",),
    ),
    "prepare_correction": SpineMilestone(
        "prepare_correction",
        "What correction does the recorded evidence support?",
        ("update_incident_report",),
    ),
}

ADVANCES = {
    ("locate_pressure", "writer_activity"): "identify_workload",
    ("identify_workload", "migration_job"): "identify_trigger",
    ("identify_trigger", "pipeline_trigger"): "prepare_correction",
}


@dataclass
class TaskSpine:
    purpose: str
    current_milestone: str
    accepted_milestones: tuple[str, ...] = ()

    @property
    def current(self) -> SpineMilestone:
        return MILESTONES[self.current_milestone]

    def admit_task(self, task_id: str) -> None:
        if task_id not in self.current.allowed_tasks:
            raise SpineTransitionRefused(
                f"outside_active_milestone:{self.current_milestone}:{task_id}"
            )

    def advance(self, evidence_key: str) -> None:
        next_milestone = ADVANCES.get((self.current_milestone, evidence_key))
        if next_milestone is None:
            raise SpineTransitionRefused(
                f"evidence_does_not_advance:{self.current_milestone}:{evidence_key}"
            )
        self.accepted_milestones = (*self.accepted_milestones, self.current_milestone)
        self.current_milestone = next_milestone

    def to_data(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_data(cls, data: dict[str, object]) -> "TaskSpine":
        return cls(
            purpose=str(data["purpose"]),
            current_milestone=str(data["current_milestone"]),
            accepted_milestones=tuple(str(item) for item in data["accepted_milestones"]),
        )


@dataclass(frozen=True)
class ReportEvidenceSelection:
    included: tuple[tuple[str, str], ...]
    excluded: tuple[tuple[str, str], ...]


class ReportSupportPolicy:
    """Selects recorded evidence connected to accepted causal milestones."""

    EVIDENCE_BY_MILESTONE = {
        "locate_pressure": (
            "service_timeouts",
            "database_write_latency",
            "application_cpu",
            "database_topology",
            "writer_activity",
        ),
        "identify_workload": ("migration_job",),
        "identify_trigger": ("pipeline_trigger",),
        "prepare_correction": (),
    }

    def select(
        self,
        spine: TaskSpine,
        recorded_evidence: dict[str, str],
    ) -> ReportEvidenceSelection:
        allowed: list[str] = []
        for milestone_id in spine.accepted_milestones:
            allowed.extend(self.EVIDENCE_BY_MILESTONE[milestone_id])
        allowed_set = set(allowed)
        included = tuple(
            (key, recorded_evidence[key])
            for key in allowed
            if key in recorded_evidence
        )
        excluded = tuple(
            (key, value)
            for key, value in sorted(recorded_evidence.items())
            if key not in allowed_set
        )
        return ReportEvidenceSelection(included, excluded)


def orders_spine() -> TaskSpine:
    return TaskSpine(
        purpose="Explain the Orders timeouts and record a supported correction.",
        current_milestone="locate_pressure",
    )


class TaskSpineStore:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS task_spines "
            "(run_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )

    def save(self, run_id: str, spine: TaskSpine) -> None:
        self.connection.execute(
            "INSERT INTO task_spines(run_id, payload) VALUES(?, ?) "
            "ON CONFLICT(run_id) DO UPDATE SET payload=excluded.payload",
            (run_id, json.dumps(spine.to_data())),
        )
        self.connection.commit()

    def load(self, run_id: str) -> TaskSpine:
        row = self.connection.execute(
            "SELECT payload FROM task_spines WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            raise KeyError(run_id)
        return TaskSpine.from_data(json.loads(row[0]))

