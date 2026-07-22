from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from orders_investigation.runtime.boundary import ORDERS_BOUNDARY
from orders_investigation.context.surface import build_decision_surface
from orders_investigation.runtime.contracts.admission import Invocation, admit
from orders_investigation.domain.incident import Incident, opening_incident
from orders_investigation.memory.store import KnowledgeRecord, KnowledgeStore
from orders_investigation.decisions.model import DecisionReceipt, OpenAIChoiceModel, build_model_request
from orders_investigation.environment.scenario import current_case
from orders_investigation.graph.spine import SpineTransitionRefused, orders_spine
from orders_investigation.graph.tasks import InvestigationGraph, opening_graph


ScenarioFactory = Callable[[], tuple[Incident, InvestigationGraph]]

SCENARIOS: dict[str, ScenarioFactory] = {
    "chapter-03": lambda: (opening_incident(), opening_graph()),
    "chapter-05": current_case,
    "chapter-11-current": current_case,
    "chapter-11-memory": current_case,
    "chapter-11-spine": current_case,
}


def load_scenario(name: str) -> tuple[Incident, InvestigationGraph]:
    return SCENARIOS[name]()


def build_surface_for_scenario(
    scenario: str,
    incident: Incident,
    graph: InvestigationGraph,
):
    if not scenario.startswith("chapter-11"):
        return build_decision_surface(incident, graph)

    retrieved: tuple[dict[str, str], ...] = ()
    if scenario in {"chapter-11-memory", "chapter-11-spine"}:
        import sqlite3

        connection = sqlite3.connect(":memory:")
        store = KnowledgeStore(connection)
        store.add(KnowledgeRecord(
            service="orders-api",
            environment="orders-production",
            evidence_gap="pipeline_trigger",
            finding="A prior Orders migration was launched by a deployment pipeline run.",
            source_run_id="run-1042",
            source_evidence=("migration_job", "pipeline_trigger"),
            reviewed=True,
        ))
        found = store.search(
            "deployment",
            service=incident.service,
            environment=incident.environment,
            missing_evidence=tuple(key.value for key in incident.missing_evidence),
        )
        connection.close()
        retrieved = tuple({
            "finding": item.record.finding,
            "source_run_id": item.record.source_run_id,
            "relevant_to": item.record.evidence_gap,
        } for item in found)

    active_direction = None
    if scenario == "chapter-11-spine":
        spine = orders_spine()
        spine.advance("writer_activity")
        spine.advance("migration_job")
        active_direction = {
            "question": spine.current.question,
            "allowed_tasks": list(spine.current.allowed_tasks),
        }

    return build_decision_surface(
        incident,
        graph,
        retrieved_knowledge=retrieved,
        active_direction=active_direction,
        max_chars=5000,
    )


def evaluate_admission(
    receipt: DecisionReceipt,
    graph: InvestigationGraph,
) -> dict[str, object]:
    try:
        invocation: Invocation = admit(receipt.choice, graph, ORDERS_BOUNDARY)
    except ValueError as exc:
        return {
            "status": "refused",
            "reason": str(exc),
            "invocation": None,
        }
    return {
        "status": "admitted",
        "reason": None,
        "invocation": invocation.model_dump(),
    }


def evaluate_boundary(
    receipt: DecisionReceipt,
    graph: InvestigationGraph,
) -> dict[str, object]:
    task = graph.tasks.get(receipt.choice.task_id)
    if task is None:
        return {
            "kind": "boundary",
            "status": "refused",
            "reason": "unknown_observation",
            "request": None,
        }
    if not ORDERS_BOUNDARY.allows(task.request):
        return {
            "kind": "boundary",
            "status": "refused",
            "reason": "request_outside_boundary",
            "request": None,
        }
    return {
        "kind": "boundary",
        "status": "permitted",
        "reason": None,
        "request": asdict(task.request),
    }


def evaluate_post_response(
    scenario: str,
    receipt: DecisionReceipt,
    graph: InvestigationGraph,
) -> dict[str, object]:
    if scenario == "chapter-03":
        return evaluate_boundary(receipt, graph)
    if scenario == "chapter-11-spine":
        admission = evaluate_admission(receipt, graph)
        if admission["status"] != "admitted":
            return {"kind": "admission", **admission}
        spine = orders_spine()
        spine.advance("writer_activity")
        spine.advance("migration_job")
        try:
            spine.admit_task(receipt.choice.task_id)
        except SpineTransitionRefused as exc:
            return {
                "kind": "direction",
                "status": "refused",
                "reason": str(exc),
                "invocation": admission["invocation"],
            }
        return {
            "kind": "direction",
            "status": "admitted",
            "reason": None,
            "invocation": admission["invocation"],
        }
    return {
        "kind": "admission",
        **evaluate_admission(receipt, graph),
    }


def build_record(
    scenario: str,
    receipt: DecisionReceipt,
    incident: Incident,
    graph: InvestigationGraph,
) -> dict[str, object]:
    surface = build_surface_for_scenario(scenario, incident, graph)
    return {
        "record_kind": "observed_live_model_call",
        "scenario": scenario,
        "decision_surface_included": list(surface.included),
        "decision_surface_omitted": list(surface.omitted),
        **asdict(receipt),
        "deterministic_result": evaluate_post_response(scenario, receipt, graph),
    }


def build_failure_record(
    scenario: str,
    model: str,
    incident: Incident,
    graph: InvestigationGraph,
    error: Exception,
    *,
    observed_at: str,
    elapsed_ms: int,
) -> dict[str, object]:
    surface = build_surface_for_scenario(scenario, incident, graph)
    request = build_model_request(surface.prompt)
    body = getattr(error, "body", None)
    provider_error = body if isinstance(body, dict) else {}
    return {
        "record_kind": "observed_live_model_failure",
        "scenario": scenario,
        "source": "openai",
        "model": model,
        "observed_at": observed_at,
        "elapsed_ms": elapsed_ms,
        "instructions": request.instructions,
        "input_text": request.input_text,
        "choice": None,
        "raw_output": None,
        "response_id": getattr(error, "request_id", None),
        "decision_surface_included": list(surface.included),
        "decision_surface_omitted": list(surface.omitted),
        "failure": {
            "exception": type(error).__name__,
            "status_code": getattr(error, "status_code", None),
            "code": provider_error.get("code"),
            "type": provider_error.get("type"),
            "message": provider_error.get("message") or str(error),
        },
        "deterministic_result": {
            "kind": "none",
            "status": "not_evaluated",
            "reason": "model_choice_not_returned",
        },
    }


def emit_record(record: dict[str, object], output: Path | None) -> None:
    rendered = json.dumps(record, indent=2, sort_keys=True)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(output)
    else:
        print(rendered)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Make one live model call and preserve the application supplied request and observed response."
    )
    parser.add_argument(
        "--scenario",
        required=True,
        choices=tuple(SCENARIOS),
        help="Exact investigation state supplied to the model",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON record destination")
    parser.add_argument("--model", help="Explicit provider model identifier; defaults to ORDERS_MODEL")
    args = parser.parse_args()

    incident, graph = load_scenario(args.scenario)
    surface = build_surface_for_scenario(args.scenario, incident, graph)
    model = args.model or "configured-by-ORDERS_MODEL"
    started = time.perf_counter()
    observed_at = datetime.now(timezone.utc).isoformat()
    try:
        receipt = OpenAIChoiceModel(args.model).choose(surface.prompt)
    except Exception as exc:
        failure = build_failure_record(
            args.scenario,
            model,
            incident,
            graph,
            exc,
            observed_at=observed_at,
            elapsed_ms=round((time.perf_counter() - started) * 1000),
        )
        emit_record(failure, args.output)
        raise SystemExit(1) from None
    record = build_record(args.scenario, receipt, incident, graph)
    emit_record(record, args.output)


if __name__ == "__main__":
    main()

