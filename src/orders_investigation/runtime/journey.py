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
