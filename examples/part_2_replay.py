"""Replay the Chapter 8-14 responsibilities as one complete investigation."""

import json
import sqlite3
from datetime import datetime, timedelta, timezone

from orders_investigation.decisions.model import ModelChoice
from orders_investigation.domain.incident import Evidence, EvidenceKey
from orders_investigation.effects.idempotency import (
    ReportEffectService,
    ResponseLost,
    report_update_intent,
)
from orders_investigation.effects.reconciliation import (
    EffectAttempt,
    EffectOutcome,
    reconcile,
)
from orders_investigation.environment.scenario import current_case
from orders_investigation.graph.spine import orders_spine
from orders_investigation.integrations.dependencies import (
    DependencyResult,
    EvidencePolicy,
    EvidenceValueKind,
    admit_evidence,
)
from orders_investigation.memory.store import KnowledgeStore, seed_reviewed_knowledge
from orders_investigation.runtime.boundary import ORDERS_BOUNDARY
from orders_investigation.runtime.contracts.admission import admit
from orders_investigation.runtime.ownership import ClaimStore
from orders_investigation.runtime.sandbox import ExecutorResult, admit_execution, make_request
from orders_investigation.runtime.workflow import SQLiteRunStore


def main() -> None:
    now = datetime(2026, 7, 21, 16, 0, tzinfo=timezone.utc)
    connection = sqlite3.connect(":memory:")
    memory = KnowledgeStore(connection)
    seed_reviewed_knowledge(memory)
    retrieved = memory.search(
        "migration",
        service="orders-api",
        environment="orders-production",
        missing_evidence=("writer_activity",),
    )

    incident, graph = current_case()
    spine = orders_spine()
    spine.advance("writer_activity")
    spine.advance("migration_job")
    choice = ModelChoice(
        "inspect_pipeline_run",
        "Inspect the deployment record named by the migration.",
        "the trigger and its configuration",
    )
    invocation = admit(choice, graph, ORDERS_BOUNDARY)
    spine.admit_task(invocation.task_id)

    claims = ClaimStore(connection)
    claims.add_ready(invocation.task_id)
    claim = claims.claim(invocation.task_id, "worker-a", now=100, lease_seconds=10)
    result = DependencyResult(
        "deployment-pipeline",
        "deploy-882",
        now - timedelta(seconds=5),
        "ok",
        {"trigger": "orders-search-backfill", "worker_count": 4},
    )
    envelope = admit_evidence(
        result,
        EvidencePolicy(
            timedelta(seconds=60),
            ("trigger", "worker_count"),
            (("trigger", EvidenceValueKind.IDENTIFIER),),
        ),
        now=now,
    )
    claims.commit(claim, "dependency result admitted", now=101)
    evidence = Evidence(
        EvidenceKey.PIPELINE_TRIGGER,
        "deploy-882 launched orders-search-backfill; worker count remained 4",
        envelope.source_system,
    )
    incident.record_evidence(evidence)
    graph.succeed(invocation.task_id, evidence)

    image = "sha256:" + "a" * 64
    request = make_request(b"analysis code", b"evidence bundle")
    artifact = json.dumps(
        {
            "analysis_id": request.analysis_id,
            "artifact_schema": request.artifact_schema,
            "request_digest": request.digest,
            "input_sha256": request.input_sha256,
            "image_digest": image,
            "findings": ["Writer pressure rises after the migration starts."],
        }
    ).encode()
    artifact_decision = admit_execution(
        ExecutorResult(0, artifact_bytes=artifact),
        request,
        image_digest=image,
    )

    effects = ReportEffectService(connection)
    key = "report-update:run-1077:1"
    try:
        effects.apply(report_update_intent(), idempotency_key=key, lose_response=True)
    except ResponseLost:
        pass
    recovered_effect = reconcile(
        effects,
        EffectAttempt(
            key,
            True,
            "timeout_local_wait_cancelled",
            EffectOutcome.UNKNOWN,
        ),
    )
    incident.report_saved = recovered_effect.effect_outcome is EffectOutcome.SUCCEEDED
    SQLiteRunStore(connection).save("run-1077", incident, graph)
    restored, _, _ = SQLiteRunStore(connection).load_full("run-1077")

    print("PART 2 REPLAY")
    print("retrieved knowledge        ", len(retrieved))
    print("proposal                    ", choice.task_id)
    print("fencing token               ", claim.fencing_token)
    print("dependency freshness        ", int(envelope.freshness_seconds), "seconds")
    print("artifact outcome            ", artifact_decision.outcome.value)
    print("artifact became authority   False")
    print("after local timeout         unknown")
    print("after reconciliation        ", recovered_effect.effect_outcome.value)
    print("recorded evidence           ", len(restored.recorded_evidence))
    print("investigation complete      ", restored.investigation_complete)


if __name__ == "__main__":
    main()
