"""Replay the complete Chapter 1-7 foundation as one connected trace."""

import sqlite3

from orders_investigation.decisions.budget import (
    AttemptOutcome,
    DecisionBudget,
    DecisionLedger,
    ModelAttempt,
)
from orders_investigation.decisions.model import ModelChoice
from orders_investigation.domain.incident import Evidence, EvidenceKey, opening_incident
from orders_investigation.environment.scenario import current_case
from orders_investigation.runtime.boundary import ORDERS_BOUNDARY
from orders_investigation.runtime.contracts.admission import admit
from orders_investigation.runtime.workflow import (
    SQLiteRunStore,
    replay_pipeline_observation,
)


def main() -> None:
    opening = opening_incident()
    gaps_before = opening.missing_evidence
    opening.record_evidence(
        Evidence(
            EvidenceKey.CONNECTION_POOL,
            "42 of 100 connections in use",
            "database_monitoring",
        )
    )

    incident, graph = current_case()
    choice = ModelChoice(
        "inspect_pipeline_run",
        "deploy-882 probably increased migration parallelism.",
        "the trigger and its configuration",
    )
    invocation = admit(choice, graph, ORDERS_BOUNDARY)
    result = replay_pipeline_observation(invocation.model_dump())
    evidence = Evidence(
        EvidenceKey(result["key"]),
        result["value"],
        result["source"],
    )
    incident.record_evidence(evidence)
    graph.succeed(invocation.task_id, evidence)

    ledger = DecisionLedger(DecisionBudget(max_retries=1))
    ledger.record(ModelAttempt(AttemptOutcome.TIMEOUT, elapsed_ms=4_000))
    ledger.record(ModelAttempt(AttemptOutcome.TIMEOUT, elapsed_ms=4_000))

    connection = sqlite3.connect(":memory:")
    SQLiteRunStore(connection).save("run-1042", incident, graph, ledger)
    restored, _, restored_ledger = SQLiteRunStore(connection).load_full("run-1042")

    print("FOUNDATION REPLAY")
    print(
        "completion gaps closed     ",
        len(gaps_before) - len(opening.missing_evidence),
    )
    print("revised hypothesis         ", restored.hypothesis)
    print(
        "parallelism claim          ",
        "not recorded as evidence"
        if "increased migration parallelism"
        not in {item.value for item in restored.recorded_evidence.values()}
        else "incorrectly recorded",
    )
    print("model attempts             ", len(restored_ledger.attempts))
    print("recovered effect status    unknown")


if __name__ == "__main__":
    main()
