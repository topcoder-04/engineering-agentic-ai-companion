"""The cumulative Orders investigation path used by late-chapter composition tests."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from orders_investigation.context.surface import build_decision_surface
from orders_investigation.decisions.model import ModelChoice
from orders_investigation.domain.incident import Evidence, EvidenceKey
from orders_investigation.effects.enforcement import (
    EffectCommand,
    EffectContext,
    EnforcedReportStore,
    GuardrailRefused,
)
from orders_investigation.environment.scenario import current_case
from orders_investigation.evaluation.production import (
    EvaluationCase,
    EvaluationResult,
    ReleaseDecision,
    ReleaseThresholds,
    SemanticTrace,
    TraceEvent,
    digest,
    evaluate,
    gate_release,
)
from orders_investigation.governance.approval import (
    ApprovalDecision,
    ApprovalIntent,
    ApprovalRequest,
    ApprovalSignal,
    ApprovalStore,
)
from orders_investigation.governance.authority import (
    AuthorizedEffect,
    DelegatedGrant,
    SessionClaims,
    VerificationEvidence,
    authorize_effect,
    verify_session,
)
from orders_investigation.governance.policy import PolicyFacts, orders_report_policy
from orders_investigation.operations.probes import Variation, variation_matrix
from orders_investigation.platform.identity import AgentContract, AgentRegistry
from orders_investigation.platform.capabilities import CapabilityProfile, admit_contract
from orders_investigation.platform.authority import (
    CallerIdentity,
    Delegation,
    authorize as authorize_caller,
)
from orders_investigation.platform.placement import DataBoundary, ExecutionTarget, place
from orders_investigation.platform.defaults import ScaffoldRequest, admit_scaffold, scaffold
from orders_investigation.platform.releases import ConformanceReceipt, release_conforms
from orders_investigation.platform.lifecycle import LifecycleOwnership, validate_ownership
from orders_investigation.runtime.boundary import ORDERS_BOUNDARY
from orders_investigation.runtime.contracts.admission import admit
from orders_investigation.runtime.workflow import replay_pipeline_observation


NOW = datetime(2026, 7, 21, 16, 5, tzinfo=timezone.utc)
ISSUER = "https://login.example.invalid"
AUDIENCE = "orders-investigation"
REPORT = "orders-incident-report"
REPORT_CONTENT = "Order completion recovered; mark customer impact resolved."


@dataclass(frozen=True)
class JourneyStep:
    kind: str
    component: str
    input_value: str
    output_value: str
    evidence_ids: tuple[str, ...] = ()
    decision_reason: str = ""


@dataclass(frozen=True)
class JourneyResult:
    completed: bool
    refusal: str | None
    report_version: int
    report_content: str
    steps: tuple[JourneyStep, ...]
    recorded_evidence: tuple[str, ...]


@dataclass(frozen=True)
class VariationRun:
    variation: Variation
    journey: JourneyResult
    evaluation: EvaluationResult


@dataclass(frozen=True)
class RegisteredRun:
    contract: AgentContract
    manifest_digest: str
    journey: JourneyResult


@dataclass(frozen=True)
class PlacedRun:
    target_id: str
    registered: RegisteredRun


def orders_agent_contract(version: str = "1") -> AgentContract:
    return AgentContract(
        "orders-investigator",
        version,
        "orders-oncall",
        "goal/v1",
        "trace/v2",
        ("database.read/v2",),
        "consequential/v4",
        "reasoning-restricted",
        frozenset({"restricted"}),
    )


def orders_capability_profile() -> CapabilityProfile:
    return CapabilityProfile(
        "orders-read-and-report",
        frozenset({"reasoning-restricted"}),
        frozenset({"database.read/v2"}),
        frozenset({"consequential/v4"}),
        frozenset({"restricted"}),
    )


def orders_caller() -> CallerIdentity:
    return CallerIdentity("user-7", "tenant-orders", frozenset({"operator"}))


def orders_delegation(*, action: str = "report.write") -> Delegation:
    return Delegation(
        "delegation-orders-report",
        "user-7",
        "tenant-orders",
        "orders-investigator",
        frozenset({action}),
        NOW + timedelta(minutes=5),
    )


def orders_data_boundary(*, region: str = "us-west-2") -> DataBoundary:
    return DataBoundary("tenant-orders", "restricted", region, 7)


def orders_execution_targets() -> tuple[ExecutionTarget, ...]:
    return (
        ExecutionTarget(
            "orders-us-west-2",
            "tenant-orders",
            frozenset({"restricted"}),
            "us-west-2",
            7,
        ),
    )


def run_registered_orders_investigation(
    registry: AgentRegistry,
    *,
    agent_id: str = "orders-investigator",
    version: str = "1",
) -> RegisteredRun:
    """Resolve an exact workload identity before any investigation work begins."""
    contract = registry.resolve(agent_id, version)
    return RegisteredRun(contract, contract.manifest_digest, run_orders_investigation())


def run_capability_admitted_orders_investigation(
    registry: AgentRegistry,
    profile: CapabilityProfile,
) -> RegisteredRun:
    """Admit the resolved contract before the investigation may execute."""
    contract = registry.resolve("orders-investigator", "1")
    reasons = admit_contract(contract, profile)
    if reasons:
        raise ValueError("capability_refused:" + ",".join(reasons))
    return run_registered_orders_investigation(registry)


def run_delegated_orders_investigation(
    identity: CallerIdentity,
    delegation: Delegation,
    *,
    action: str = "report.write",
) -> RegisteredRun:
    """Carry the caller's exact delegated authority into the Orders work."""
    allowed, reasons = authorize_caller(
        identity,
        delegation,
        "orders-investigator",
        action,
        NOW,
    )
    if not allowed:
        raise ValueError("caller_authority_refused:" + ",".join(reasons))
    registry = AgentRegistry()
    registry.register(orders_agent_contract())
    return run_capability_admitted_orders_investigation(
        registry, orders_capability_profile()
    )


def run_placed_orders_investigation(
    boundary: DataBoundary,
    targets: tuple[ExecutionTarget, ...],
) -> PlacedRun:
    """Select an exact data-safe target before carrying caller authority."""
    target_id = place(boundary, targets)
    registered = run_delegated_orders_investigation(
        orders_caller(), orders_delegation()
    )
    return PlacedRun(target_id, registered)


def run_scaffolded_orders_investigation(
    *,
    overrides: dict[str, str] | None = None,
    approved_exceptions: tuple[str, ...] = (),
) -> PlacedRun:
    """Admit the paved project shape before placement and runtime work."""
    project = scaffold(
        ScaffoldRequest(
            "orders-investigator", "orders-oncall", "orders-read-and-report"
        ),
        overrides,
    )
    reasons = admit_scaffold(project, approved_exceptions=approved_exceptions)
    if reasons:
        raise ValueError("scaffold_refused:" + ",".join(reasons))
    return run_placed_orders_investigation(
        orders_data_boundary(), orders_execution_targets()
    )


def orders_conformance_receipt(
    *,
    candidate_digest: str = "candidate-orders-v1",
) -> ConformanceReceipt:
    return ConformanceReceipt(
        candidate_digest,
        orders_agent_contract().manifest_digest,
        "suite-5",
        frozenset({"trace", "policy", "rollback", "authority", "placement"}),
        frozenset(),
    )


def run_conformant_orders_investigation(
    candidate_digest: str,
    receipt: ConformanceReceipt,
) -> PlacedRun:
    """Bind conformance evidence to the candidate before executing it."""
    allowed, reasons = release_conforms(
        candidate_digest,
        orders_agent_contract(),
        receipt,
        {"trace", "policy", "rollback", "authority", "placement"},
        required_suite_version="suite-5",
    )
    if not allowed:
        raise ValueError("conformance_refused:" + ",".join(reasons))
    return run_scaffolded_orders_investigation()


def orders_lifecycle_ownership(*, owner: str = "orders-oncall") -> LifecycleOwnership:
    return LifecycleOwnership(
        "orders-investigator",
        "1",
        owner,
        "runbooks/orders-investigator.md",
        "orders-release-oncall",
    )


def run_owned_orders_investigation(ownership: LifecycleOwnership) -> PlacedRun:
    """Require durable operating and rollback ownership before execution."""
    allowed, reasons = validate_ownership(ownership)
    if not allowed:
        raise ValueError("lifecycle_refused:" + ",".join(reasons))
    receipt = orders_conformance_receipt()
    return run_conformant_orders_investigation("candidate-orders-v1", receipt)


def trace_orders_investigation(
    result: JourneyResult,
    *,
    execution_id: str = "orders-run",
) -> SemanticTrace:
    """Turn the events emitted by the real journey into a semantic trace."""
    events = tuple(
        TraceEvent(
            sequence=index,
            kind=step.kind,
            component=step.component,
            input_digest=digest(step.input_value),
            output_digest=digest(step.output_value),
            evidence_ids=step.evidence_ids,
            decision_reason=step.decision_reason,
            duration_ms=10,
            input_units=5,
            output_units=5,
            data_class="restricted",
        )
        for index, step in enumerate(result.steps, start=1)
    )
    return SemanticTrace(
        execution_id,
        "orders-agent-v1",
        "reasoning-restricted",
        "orders-report-v1",
        events,
        "completed" if result.completed else "refused",
    )


def evaluate_orders_investigation(result: JourneyResult) -> EvaluationResult:
    """Evaluate the trace produced by this exact investigation outcome."""
    trace = trace_orders_investigation(result)
    case = EvaluationCase(
        "orders-recovery",
        frozenset(result.recorded_evidence),
        frozenset({"observe", "decide", "effect"}),
        maximum_actions=4,
    )
    return evaluate(trace, case)


def gate_orders_release(results: tuple[JourneyResult, ...]) -> ReleaseDecision:
    """Gate a candidate using evaluations and traces from executed journeys."""
    return gate_release(
        tuple(evaluate_orders_investigation(result) for result in results),
        tuple(trace_orders_investigation(result) for result in results),
        ReleaseThresholds(minimum_pass_rate=1.0),
    )


def run_orders_variations() -> tuple[VariationRun, ...]:
    """Execute the Orders path across stable model, fault, and timing variations."""
    variations = variation_matrix(
        ("reasoning-small", "reasoning-large"),
        ("none", "stale_evidence"),
        (0, 500),
    )
    runs = []
    for variation in variations:
        journey = run_orders_investigation(
            evidence_current=variation.dependency_fault != "stale_evidence"
        )
        runs.append(
            VariationRun(variation, journey, evaluate_orders_investigation(journey))
        )
    return tuple(runs)


def _approve(intent: ApprovalIntent, connection: sqlite3.Connection) -> str:
    approvals = ApprovalStore(connection)
    request = ApprovalRequest(
        "approval-orders-recovery",
        "orders-run",
        1,
        "publish-recovery",
        intent,
        NOW,
        NOW + timedelta(minutes=10),
    )
    approvals.create(request)
    receipt = approvals.deliver(
        ApprovalSignal(
            "approval-signal-orders-recovery",
            request.approval_id,
            intent.digest,
            ApprovalDecision.APPROVE,
            NOW + timedelta(minutes=1),
        )
    )
    return receipt.status.value


def _authorize(intent: ApprovalIntent, approval_status: str) -> bool:
    session = verify_session(
        SessionClaims(
            ISSUER,
            "person-204",
            AUDIENCE,
            "session-551",
            NOW + timedelta(minutes=20),
        ),
        VerificationEvidence(True, True),
        expected_issuer=ISSUER,
        expected_audience=AUDIENCE,
        now=NOW,
    )
    receipt = authorize_effect(
        session,
        DelegatedGrant(
            "grant-orders-recovery-publish",
            session.subject,
            session.session_id,
            AUDIENCE,
            "publish_recovery_update",
            REPORT,
            intent.digest,
            NOW - timedelta(minutes=1),
            NOW + timedelta(minutes=10),
        ),
        AuthorizedEffect(
            "approval-orders-recovery",
            approval_status,
            "publish_recovery_update",
            REPORT,
            intent.digest,
        ),
        expected_audience=AUDIENCE,
        now=NOW,
    )
    return receipt.intent_digest == intent.digest


def run_orders_investigation(*, evidence_current: bool = True) -> JourneyResult:
    """Run one bounded proposal through the real report-write boundary.

    The refusal switch represents evidence becoming stale after proposal admission.
    The effect boundary must notice that change and leave the report untouched.
    """
    incident, graph = current_case()
    surface = build_decision_surface(incident, graph)
    choice = ModelChoice(
        "inspect_pipeline_run",
        "Inspect the deployment that launched the migration.",
        "the trigger and its configuration",
    )
    invocation = admit(choice, graph, ORDERS_BOUNDARY)
    raw = replay_pipeline_observation(invocation.model_dump())
    evidence = Evidence(EvidenceKey(raw["key"]), raw["value"], raw["source"])
    incident.record_evidence(evidence)
    graph.succeed(invocation.task_id, evidence)

    evidence_ids = tuple(sorted(key.value for key in incident.recorded_evidence))
    intent = ApprovalIntent(
        "publish_recovery_update",
        REPORT,
        REPORT_CONTENT,
        evidence_ids,
    )
    connection = sqlite3.connect(":memory:")
    approval_status = _approve(intent, connection)
    authorization_admitted = _authorize(intent, approval_status)
    facts = PolicyFacts(
        "orders",
        "production",
        "publish_recovery_update",
        REPORT,
        approval_status,
        authorization_admitted,
        evidence_current,
        "recovered",
    )
    policy = orders_report_policy()
    store = EnforcedReportStore(connection)
    store.seed_report(REPORT, 7, "Investigating recovery.")
    store.activate_policy(policy.version)
    command = EffectCommand(
        "report-effect-orders-recovery",
        facts.operation,
        facts.resource,
        REPORT_CONTENT,
        intent.digest,
        7,
        policy.decide(facts),
        policy.rules[0].obligations,
        evidence_ids,
    )

    steps = (
        JourneyStep(
            "observe",
            "orders",
            "opening incident",
            incident.hypothesis,
            tuple(sorted(key.value for key in incident.recorded_evidence if key != evidence.key)),
        ),
        JourneyStep(
            "decide",
            "orders",
            surface.prompt,
            invocation.task_id,
            decision_reason=choice.reason,
        ),
        JourneyStep(
            "observe",
            invocation.source,
            invocation.resource,
            evidence.value,
            (evidence.key.value,),
        ),
    )
    try:
        receipt = store.apply(command, EffectContext(facts, intent.digest), policy)
    except GuardrailRefused as exc:
        version, content = store.report(REPORT)
        return JourneyResult(
            False,
            str(exc),
            version,
            content,
            steps + (
                JourneyStep(
                    "effect_refused",
                    "orders-report",
                    intent.digest,
                    str(exc),
                    evidence_ids,
                    "effect boundary rechecked current facts",
                ),
            ),
            evidence_ids,
        )

    incident.report_saved = True
    version, content = store.report(REPORT)
    return JourneyResult(
        incident.investigation_complete,
        None,
        version,
        content,
        steps + (
            JourneyStep(
                "effect",
                "orders-report",
                intent.digest,
                receipt.effect_id,
                evidence_ids,
                "approved authority and current evidence",
            ),
        ),
        evidence_ids,
    )
