import importlib.util
import inspect
import sqlite3

from orders_investigation.decisions.budget import (
    AttemptOutcome,
    DecisionBudget,
    DecisionLedger,
    ModelAttempt,
)
from orders_investigation.domain.incident import EvidenceKey, Evidence, opening_incident
from orders_investigation.graph.tasks import opening_graph
from orders_investigation.environment.scenario import current_case
from orders_investigation.runtime.workflow import GraphState, SQLiteRunStore, build_langgraph, invoke_langgraph


def test_close_and_reopen_restores_expanded_work(tmp_path):
    path = tmp_path / "orders-investigation.sqlite"
    first = sqlite3.connect(path)
    incident = opening_incident()
    graph = opening_graph()
    topology = Evidence(
        EvidenceKey.DATABASE_TOPOLOGY,
        "writer=orders-db-w1; replica=orders-db-r1",
        "database_monitoring",
    )
    incident.record_evidence(topology)
    graph.succeed("inspect_database_topology", topology)
    writer_activity = Evidence(
        EvidenceKey.WRITER_ACTIVITY,
        "orders-search-backfill consumes most write capacity",
        "database_monitoring",
    )
    incident.record_evidence(writer_activity)
    graph.succeed("inspect_writer_activity", writer_activity)
    migration = Evidence(
        EvidenceKey.MIGRATION_JOB,
        "started at 1:58 p.m. by deploy-882",
        "migration_jobs",
    )
    incident.record_evidence(migration)
    graph.succeed("inspect_migration_job", migration)
    ledger = DecisionLedger(DecisionBudget())
    ledger.record(ModelAttempt(AttemptOutcome.TIMEOUT, elapsed_ms=4_000))
    SQLiteRunStore(first).save("run-1042", incident, graph, ledger)
    first.close()

    second = sqlite3.connect(path)
    restored_incident, restored_graph, restored_ledger = SQLiteRunStore(second).load_full("run-1042")
    second.close()
    assert restored_incident.recorded_evidence[EvidenceKey.DATABASE_TOPOLOGY].value.startswith("writer=")
    assert {"inspect_pipeline_run", "inspect_replication_delay"} <= set(restored_graph.ready_ids())
    assert restored_ledger is not None
    assert len(restored_ledger.attempts) == 1
    assert restored_ledger.total_elapsed_ms == 4_000


def test_checkpoint_cannot_invent_report_success_after_crash(tmp_path):
    path = tmp_path / "report-crash.sqlite"
    first = sqlite3.connect(path)
    incident = opening_incident()
    graph = opening_graph()
    SQLiteRunStore(first).save("run-1042", incident, graph, DecisionLedger(DecisionBudget()))
    first.close()

    # The illustrative report service accepted the request here, but the process
    # stopped before a successful result was stored.
    second = sqlite3.connect(path)
    restored_incident, _, _ = SQLiteRunStore(second).load_full("run-1042")
    second.close()
    assert not restored_incident.report_saved


def test_langgraph_state_names_persisted_responsibilities_without_outside_effect_truth():
    incident, graph = current_case()
    state: GraphState = {
        "run_id": "run-1042",
        "tasks": graph.to_data(),
        "ready_tasks": [],
        "recorded_evidence": {
            key.value: evidence.value for key, evidence in incident.recorded_evidence.items()
        },
        "missing_evidence": [key.value for key in incident.missing_evidence],
        "report_saved": incident.report_saved,
        "decision_ledger": DecisionLedger(DecisionBudget()).to_data(),
        "proposal": {
            "task_id": "inspect_pipeline_run",
            "reason": "Inspect the deployment record named by the migration job.",
            "expected_evidence": "The trigger and its recorded configuration.",
        },
    }
    assert state["run_id"] == "run-1042"
    assert not state["report_saved"]


def test_langgraph_source_contains_the_complete_controlled_turn():
    source = inspect.getsource(build_langgraph)
    for node in (
        "refresh_ready_work",
        "prepare_decision_surface",
        "admit_proposal",
        "invoke_observation",
        "record_result",
        "check_completion",
    ):
        assert f'add_node("{node}"' in source
    assert "add_conditional_edges" in source


def test_langgraph_executes_the_controlled_turn_when_packages_are_available():
    if importlib.util.find_spec("langgraph") is None:
        return
    incident, graph = current_case()
    state: GraphState = {
        "run_id": "run-1042",
        "tasks": graph.to_data(),
        "ready_tasks": [],
        "recorded_evidence": {
            key.value: evidence.value for key, evidence in incident.recorded_evidence.items()
        },
        "missing_evidence": [key.value for key in incident.missing_evidence],
        "report_saved": False,
        "decision_ledger": DecisionLedger(DecisionBudget()).to_data(),
        "proposal": {
            "task_id": "inspect_pipeline_run",
            "reason": "Inspect the deployment record named by the migration job.",
            "expected_evidence": "The trigger and its recorded configuration.",
        },
    }
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    result = invoke_langgraph(connection, state, execution_id="run-1042")
    assert result["recorded_evidence"]["pipeline_trigger"].startswith("deploy-882")
    assert not result["investigation_complete"]
    connection.close()

