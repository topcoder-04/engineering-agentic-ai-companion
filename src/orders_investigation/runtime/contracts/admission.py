from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from orders_investigation.runtime.boundary import InvestigationBoundary, Request
from orders_investigation.graph.tasks import InvestigationGraph, TaskStatus

if TYPE_CHECKING:
    from orders_investigation.decisions.model import ModelChoice


class Proposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1, max_length=80)
    reason: str = Field(min_length=1, max_length=300)
    expected_evidence: str = Field(min_length=1, max_length=240)


class Invocation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str
    operation: str
    source: str
    environment: str
    resource: str
    detail: str


def admit(choice: ModelChoice, graph: InvestigationGraph, boundary: InvestigationBoundary) -> Invocation:
    proposal = Proposal.model_validate({
        "task_id": choice.task_id,
        "reason": choice.reason,
        "expected_evidence": choice.expected_evidence,
    })
    task = graph.tasks.get(proposal.task_id)
    if task is None:
        raise ValueError("unknown_task")
    graph.refresh()
    if task.status != TaskStatus.READY:
        raise ValueError("task_not_ready")
    if not boundary.allows(task.request):
        raise ValueError("request_outside_boundary")
    request: Request = task.request
    return Invocation(task_id=task.task_id, **request.__dict__)


def repair_once(raw: dict[str, object], repaired: dict[str, object]) -> Proposal:
    try:
        return Proposal.model_validate(raw)
    except ValidationError:
        return Proposal.model_validate(repaired)

