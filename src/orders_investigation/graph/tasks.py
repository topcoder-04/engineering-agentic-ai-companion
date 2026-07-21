from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum

from orders_investigation.runtime.boundary import Request
from orders_investigation.domain.incident import Evidence, EvidenceKey
from orders_investigation.environment.requests import OPENING_OBSERVATION_REQUESTS


class TaskStatus(StrEnum):
    READY = "ready"
    WAITING = "waiting"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class Task:
    task_id: str
    request: Request
    dependencies: tuple[str, ...] = ()
    status: TaskStatus = TaskStatus.WAITING


class InvestigationGraph:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}

    def add(self, task: Task) -> None:
        if task.task_id in self.tasks:
            return
        missing = [dep for dep in task.dependencies if dep not in self.tasks]
        if missing:
            raise ValueError(f"unknown_dependencies:{','.join(missing)}")
        self.tasks[task.task_id] = task
        self.refresh()

    def refresh(self) -> None:
        for task in self.tasks.values():
            if task.status in {TaskStatus.SUCCEEDED, TaskStatus.FAILED}:
                continue
            dependency_states = [self.tasks[dep].status for dep in task.dependencies]
            if all(state == TaskStatus.SUCCEEDED for state in dependency_states):
                task.status = TaskStatus.READY
            else:
                task.status = TaskStatus.WAITING

    def ready_ids(self) -> tuple[str, ...]:
        self.refresh()
        return tuple(sorted(task.task_id for task in self.tasks.values() if task.status == TaskStatus.READY))

    def succeed(self, task_id: str, evidence: Evidence) -> None:
        task = self.tasks[task_id]
        if task.status != TaskStatus.READY:
            raise ValueError("task_not_ready")
        task.status = TaskStatus.SUCCEEDED
        self.expand(evidence)
        self.refresh()

    def fail(self, task_id: str) -> None:
        task = self.tasks[task_id]
        if task.status != TaskStatus.READY:
            raise ValueError("task_not_ready")
        task.status = TaskStatus.FAILED
        self.refresh()

    def expand(self, evidence: Evidence) -> None:
        if evidence.key == EvidenceKey.DATABASE_TOPOLOGY:
            self.add(Task(
                "inspect_writer_activity",
                Request("observe", "database_monitoring", "orders-production", "orders-db-w1", "write_activity"),
                ("inspect_database_topology",),
            ))
            self.add(Task(
                "inspect_replication_delay",
                Request("observe", "database_monitoring", "orders-production", "orders-db-r1", "replication_delay"),
                ("inspect_database_topology",),
            ))
        elif evidence.key == EvidenceKey.WRITER_ACTIVITY:
            self.add(Task(
                "inspect_migration_job",
                Request("observe", "migration_jobs", "orders-production", "orders-search-backfill", "run_record"),
                ("inspect_writer_activity",),
            ))
        elif evidence.key == EvidenceKey.MIGRATION_JOB:
            self.add(Task(
                "inspect_pipeline_run",
                Request("observe", "deployment_pipeline", "orders-production", "deploy-882", "trigger_record"),
                ("inspect_migration_job",),
            ))

    def to_data(self) -> list[dict[str, object]]:
        rows = []
        for task in self.tasks.values():
            row = asdict(task)
            row["status"] = task.status.value
            rows.append(row)
        return rows

    @classmethod
    def from_data(cls, rows: list[dict[str, object]]) -> "InvestigationGraph":
        graph = cls()
        for row in rows:
            request = Request(**row["request"])
            graph.tasks[row["task_id"]] = Task(
                task_id=row["task_id"],
                request=request,
                dependencies=tuple(row["dependencies"]),
                status=TaskStatus(row["status"]),
            )
        graph.refresh()
        return graph


def opening_graph() -> InvestigationGraph:
    graph = InvestigationGraph()
    for task_id, request in OPENING_OBSERVATION_REQUESTS.items():
        graph.add(Task(task_id, request))
    return graph

