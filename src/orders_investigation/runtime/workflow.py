from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from typing import NotRequired, TypedDict

from orders_investigation.runtime.boundary import ORDERS_BOUNDARY
from orders_investigation.runtime.contracts.admission import admit
from orders_investigation.domain.incident import EvidenceKey, Incident, Evidence, HypothesisRevision
from orders_investigation.decisions.budget import DecisionLedger
from orders_investigation.decisions.model import ModelChoice
from orders_investigation.graph.tasks import InvestigationGraph


class SQLiteRunStore:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS investigation_runs "
            "(run_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )

    def save(
        self,
        run_id: str,
        incident: Incident,
        graph: InvestigationGraph,
        decision_ledger: DecisionLedger | None = None,
    ) -> None:
        payload = json.dumps({
            "incident": {
                "service": incident.service,
                "environment": incident.environment,
                "hypothesis": incident.hypothesis,
                "hypothesis_revisions": [
                    {
                        "previous": revision.previous,
                        "current": revision.current,
                        "based_on": [key.value for key in revision.based_on],
                    }
                    for revision in incident.hypothesis_revisions
                ],
                "report_saved": incident.report_saved,
                "recorded_evidence": [
                    {"key": key.value, "value": item.value, "source": item.source}
                    for key, item in incident.recorded_evidence.items()
                ],
            },
            "tasks": graph.to_data(),
            "decision_ledger": decision_ledger.to_data() if decision_ledger else None,
        })
        self.connection.execute(
            "INSERT INTO investigation_runs(run_id, payload) VALUES(?, ?) "
            "ON CONFLICT(run_id) DO UPDATE SET payload=excluded.payload",
            (run_id, payload),
        )
        self.connection.commit()

    def load(self, run_id: str) -> tuple[Incident, InvestigationGraph]:
        row = self.connection.execute(
            "SELECT payload FROM investigation_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            raise KeyError(run_id)
        payload = json.loads(row[0])
        data = payload["incident"]
        incident = Incident(
            service=data["service"],
            environment=data["environment"],
            hypothesis=data["hypothesis"],
            report_saved=data["report_saved"],
        )
        for item in data["recorded_evidence"]:
            incident.record_evidence(Evidence(EvidenceKey(item["key"]), item["value"], item["source"]))
        incident.hypothesis_revisions = [
            HypothesisRevision(
                previous=item["previous"],
                current=item["current"],
                based_on=tuple(EvidenceKey(key) for key in item["based_on"]),
            )
            for item in data.get("hypothesis_revisions", [])
        ]
        return incident, InvestigationGraph.from_data(payload["tasks"])

    def load_full(self, run_id: str) -> tuple[Incident, InvestigationGraph, DecisionLedger | None]:
        row = self.connection.execute(
            "SELECT payload FROM investigation_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            raise KeyError(run_id)
        payload = json.loads(row[0])
        incident, graph = self.load(run_id)
        ledger_data = payload.get("decision_ledger")
        ledger = DecisionLedger.from_data(ledger_data) if ledger_data else None
        return incident, graph, ledger


class GraphState(TypedDict):
    run_id: str
    tasks: list[dict[str, object]]
    ready_tasks: list[str]
    recorded_evidence: dict[str, str]
    missing_evidence: list[str]
    report_saved: bool
    decision_ledger: dict[str, object]
    proposal: dict[str, str]
    decision_surface: NotRequired[dict[str, object]]
    invocation: NotRequired[dict[str, str]]
    observation_result: NotRequired[dict[str, str]]
    admission_error: NotRequired[str]
    investigation_complete: NotRequired[bool]
    task_spine: NotRequired[dict[str, object]]


ObservationRunner = Callable[[dict[str, str]], dict[str, str]]


def replay_pipeline_observation(invocation: dict[str, str]) -> dict[str, str]:
    """Return the captured pipeline fixture for the one admitted read request."""
    if invocation["task_id"] != "inspect_pipeline_run":
        raise ValueError("replay_has_no_result_for_invocation")
    return {
        "key": EvidenceKey.PIPELINE_TRIGGER.value,
        "value": (
            "deploy-882 launched orders-search-backfill; configured worker count 4; "
            "preceding worker count 4"
        ),
        "source": "deployment_pipeline",
    }


def build_langgraph(
    connection: sqlite3.Connection,
    *,
    observe: ObservationRunner = replay_pipeline_observation,
):
    from langgraph.checkpoint.sqlite import SqliteSaver
    from langgraph.graph import END, START, StateGraph

    def refresh_ready_work(state: GraphState) -> dict[str, object]:
        graph = InvestigationGraph.from_data(state["tasks"])
        return {"ready_tasks": list(graph.ready_ids())}

    def prepare_decision_surface(state: GraphState) -> dict[str, object]:
        return {
            "decision_surface": {
                "recorded_evidence": state["recorded_evidence"],
                "missing_evidence": state["missing_evidence"],
                "ready_tasks": state["ready_tasks"],
            }
        }

    def admit_proposal(state: GraphState) -> dict[str, object]:
        graph = InvestigationGraph.from_data(state["tasks"])
        try:
            invocation = admit(ModelChoice(**state["proposal"]), graph, ORDERS_BOUNDARY)
        except (TypeError, ValueError) as exc:
            return {"admission_error": str(exc)}
        return {"invocation": invocation.model_dump(), "admission_error": ""}

    def route_after_admission(state: GraphState) -> str:
        return "refused" if state.get("admission_error") else "admitted"

    def invoke_observation(state: GraphState) -> dict[str, object]:
        return {"observation_result": observe(state["invocation"])}

    def record_result(state: GraphState) -> dict[str, object]:
        result = state["observation_result"]
        evidence = Evidence(
            EvidenceKey(result["key"]),
            result["value"],
            result["source"],
        )
        graph = InvestigationGraph.from_data(state["tasks"])
        graph.succeed(state["invocation"]["task_id"], evidence)
        recorded = dict(state["recorded_evidence"])
        recorded[evidence.key.value] = evidence.value
        missing = [key for key in state["missing_evidence"] if key != evidence.key.value]
        return {
            "tasks": graph.to_data(),
            "ready_tasks": list(graph.ready_ids()),
            "recorded_evidence": recorded,
            "missing_evidence": missing,
        }

    def check_completion(state: GraphState) -> dict[str, object]:
        return {
            "investigation_complete": not state["missing_evidence"] and state["report_saved"]
        }

    builder = StateGraph(GraphState)
    builder.add_node("refresh_ready_work", refresh_ready_work)
    builder.add_node("prepare_decision_surface", prepare_decision_surface)
    builder.add_node("admit_proposal", admit_proposal)
    builder.add_node("invoke_observation", invoke_observation)
    builder.add_node("record_result", record_result)
    builder.add_node("check_completion", check_completion)
    builder.add_edge(START, "refresh_ready_work")
    builder.add_edge("refresh_ready_work", "prepare_decision_surface")
    builder.add_edge("prepare_decision_surface", "admit_proposal")
    builder.add_conditional_edges(
        "admit_proposal",
        route_after_admission,
        {"refused": END, "admitted": "invoke_observation"},
    )
    builder.add_edge("invoke_observation", "record_result")
    builder.add_edge("record_result", "check_completion")
    builder.add_edge("check_completion", END)
    return builder.compile(checkpointer=SqliteSaver(connection))


def invoke_langgraph(
    connection: sqlite3.Connection,
    state: GraphState,
    *,
    execution_id: str,
    observe: ObservationRunner = replay_pipeline_observation,
) -> GraphState:
    """Run one controlled turn using the execution ID as LangGraph's thread ID."""
    graph = build_langgraph(connection, observe=observe)
    config = {"configurable": {"thread_id": execution_id}}
    return graph.invoke(state, config)
