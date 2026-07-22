from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CoordinationRefused(ValueError):
    pass


class Recommendation(StrEnum):
    RECOVERY_SUPPORTED = "recovery_supported"
    RECOVERY_NOT_SUPPORTED = "recovery_not_supported"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True)
class EvidenceFact:
    evidence_id: str
    key: str
    value: str


@dataclass(frozen=True)
class SpecialistAssignment:
    assignment_id: str
    run_id: str
    plan_version: int
    specialist_id: str
    task_id: str
    result_kind: str
    allowed_evidence_ids: tuple[str, ...]
    join_id: str
    max_turns: int


@dataclass(frozen=True)
class SpecialistResult:
    assignment_id: str
    run_id: str
    plan_version: int
    specialist_id: str
    task_id: str
    result_kind: str
    facts: tuple[EvidenceFact, ...]
    recommendation: Recommendation
    turns_used: int
    stop_reason: str


@dataclass(frozen=True)
class JoinContract:
    join_id: str
    run_id: str
    plan_version: int
    required_assignments: tuple[str, ...]
    proposal_id: str
    proposed_intent: str


@dataclass(frozen=True)
class JoinedProposal:
    proposal_id: str
    proposed_intent: str
    supporting_assignments: tuple[str, ...]
    supporting_evidence: tuple[str, ...]


@dataclass(frozen=True)
class JoinReceipt:
    outcome: str
    accepted_assignments: tuple[str, ...]
    missing_assignments: tuple[str, ...]
    proposal: JoinedProposal | None


@dataclass(frozen=True)
class CoordinationReceipt:
    assignments_issued: int
    results_accepted: int
    results_refused: int
    joins_attempted: int


class SpecialistCoordinator:
    def __init__(
        self,
        *,
        run_id: str,
        active_plan_version: int,
        current_tasks: frozenset[str],
        recorded_evidence: dict[str, dict[str, str]],
    ):
        self.run_id = run_id
        self.active_plan_version = active_plan_version
        self.current_tasks = current_tasks
        self.recorded_evidence = recorded_evidence
        self.assignments: dict[str, SpecialistAssignment] = {}
        self.results: dict[str, SpecialistResult] = {}
        self._results_refused = 0
        self._joins_attempted = 0

    def _refuse_result(self, reason: str) -> None:
        self._results_refused += 1
        raise CoordinationRefused(reason)

    def delegate(self, assignment: SpecialistAssignment) -> None:
        if assignment.run_id != self.run_id:
            raise CoordinationRefused("assignment_run_mismatch")
        if assignment.plan_version != self.active_plan_version:
            raise CoordinationRefused("assignment_plan_not_active")
        if assignment.task_id not in self.current_tasks:
            raise CoordinationRefused("assignment_outside_current_plan")
        if assignment.assignment_id in self.assignments:
            raise CoordinationRefused("assignment_already_exists")
        if not assignment.allowed_evidence_ids:
            raise CoordinationRefused("assignment_has_no_evidence_boundary")
        self.assignments[assignment.assignment_id] = assignment

    def accept_result(self, result: SpecialistResult) -> None:
        assignment = self.assignments.get(result.assignment_id)
        if assignment is None:
            self._refuse_result("unknown_assignment")
        assert assignment is not None
        expected = (
            assignment.run_id,
            assignment.plan_version,
            assignment.specialist_id,
            assignment.task_id,
            assignment.result_kind,
        )
        actual = (
            result.run_id,
            result.plan_version,
            result.specialist_id,
            result.task_id,
            result.result_kind,
        )
        if actual != expected:
            self._refuse_result("result_contract_mismatch")
        if result.assignment_id in self.results:
            self._refuse_result("result_already_accepted")
        if result.turns_used < 1 or result.turns_used > assignment.max_turns:
            self._refuse_result("result_turn_budget_invalid")
        if result.stop_reason != "assignment_complete":
            self._refuse_result("result_stop_reason_invalid")
        if not result.facts:
            self._refuse_result("result_has_no_evidence")

        allowed = set(assignment.allowed_evidence_ids)
        for fact in result.facts:
            if fact.evidence_id not in allowed:
                self._refuse_result("result_evidence_outside_assignment")
            recorded = self.recorded_evidence.get(fact.evidence_id)
            if recorded is None or recorded.get(fact.key) != fact.value:
                self._refuse_result("result_not_supported_by_recorded_evidence")
        self.results[result.assignment_id] = result

    def join(self, contract: JoinContract) -> JoinReceipt:
        self._joins_attempted += 1
        if contract.run_id != self.run_id:
            raise CoordinationRefused("join_run_mismatch")
        if contract.plan_version != self.active_plan_version:
            raise CoordinationRefused("join_plan_not_active")

        required = tuple(contract.required_assignments)
        for assignment_id in required:
            assignment = self.assignments.get(assignment_id)
            if assignment is None or assignment.join_id != contract.join_id:
                raise CoordinationRefused("join_assignment_mismatch")

        accepted = tuple(
            assignment_id for assignment_id in required
            if assignment_id in self.results
        )
        missing = tuple(
            assignment_id for assignment_id in required
            if assignment_id not in self.results
        )
        if missing:
            return JoinReceipt("incomplete", accepted, missing, None)

        results = tuple(self.results[assignment_id] for assignment_id in required)
        if any(
            result.recommendation != Recommendation.RECOVERY_SUPPORTED
            for result in results
        ):
            return JoinReceipt("not_supported", accepted, (), None)

        evidence_ids = tuple(dict.fromkeys(
            fact.evidence_id
            for result in results
            for fact in result.facts
        ))
        proposal = JoinedProposal(
            proposal_id=contract.proposal_id,
            proposed_intent=contract.proposed_intent,
            supporting_assignments=required,
            supporting_evidence=evidence_ids,
        )
        return JoinReceipt("joined", accepted, (), proposal)

    @property
    def receipt(self) -> CoordinationReceipt:
        return CoordinationReceipt(
            assignments_issued=len(self.assignments),
            results_accepted=len(self.results),
            results_refused=self._results_refused,
            joins_attempted=self._joins_attempted,
        )
