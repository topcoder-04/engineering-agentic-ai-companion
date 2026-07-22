import json
import sqlite3

import pytest

from orders_investigation.live_demo import (
    build_record,
    build_surface_for_scenario,
    load_scenario,
)
from orders_investigation.decisions.model import CHOICE_INSTRUCTIONS, DecisionReceipt, ModelChoice
from orders_investigation.graph.spine import (
    ReportSupportPolicy,
    SpineTransitionRefused,
    TaskSpineStore,
    orders_spine,
)


def test_graph_ready_task_can_be_outside_the_active_milestone():
    spine = orders_spine()
    spine.advance("writer_activity")

    with pytest.raises(SpineTransitionRefused, match="outside_active_milestone"):
        spine.admit_task("inspect_replication_delay")

    spine.admit_task("inspect_migration_job")


def test_evidence_advances_the_current_question():
    spine = orders_spine()
    spine.advance("writer_activity")
    spine.admit_task("inspect_migration_job")
    spine.advance("migration_job")

    assert spine.current_milestone == "identify_trigger"
    assert spine.current.question == "What introduced the migration workload?"
    assert spine.accepted_milestones == ("locate_pressure", "identify_workload")


def test_spine_survives_connection_close_and_reopen(tmp_path):
    path = tmp_path / "spine.sqlite"
    first = sqlite3.connect(path)
    spine = orders_spine()
    spine.advance("writer_activity")
    TaskSpineStore(first).save("run-1077", spine)
    first.close()

    second = sqlite3.connect(path)
    restored = TaskSpineStore(second).load("run-1077")
    second.close()

    assert restored.current_milestone == "identify_workload"
    assert restored.accepted_milestones == ("locate_pressure",)


def test_report_support_excludes_evidence_outside_accepted_causal_path():
    spine = orders_spine()
    spine.advance("writer_activity")
    spine.advance("migration_job")
    spine.advance("pipeline_trigger")
    recorded = {
        "service_timeouts": "18%",
        "database_write_latency": "4.8s",
        "writer_activity": "orders-search-backfill consumed writer capacity",
        "migration_job": "orders-search-backfill came from deploy-882",
        "pipeline_trigger": "deploy-882 launched the migration",
        "replication_delay": "45 seconds",
    }

    selection = ReportSupportPolicy().select(spine, recorded)

    assert "replication_delay" not in dict(selection.included)
    assert dict(selection.excluded) == {"replication_delay": "45 seconds"}
    assert dict(selection.included)["pipeline_trigger"] == "deploy-882 launched the migration"


def test_report_support_does_not_treat_recording_as_milestone_acceptance():
    spine = orders_spine()
    spine.advance("writer_activity")
    spine.advance("migration_job")
    selection = ReportSupportPolicy().select(
        spine,
        {
            "writer_activity": "migration consumed writer capacity",
            "migration_job": "job came from deploy-882",
            "pipeline_trigger": "deploy-882 launched the job",
        },
    )

    assert "pipeline_trigger" not in dict(selection.included)
    assert dict(selection.excluded)["pipeline_trigger"] == "deploy-882 launched the job"


def test_live_comparison_surfaces_add_memory_then_active_direction():
    incident, graph = load_scenario("chapter-11-current")
    current = json.loads(build_surface_for_scenario(
        "chapter-11-current", incident, graph
    ).prompt)
    memory = json.loads(build_surface_for_scenario(
        "chapter-11-memory", incident, graph
    ).prompt)
    spine = json.loads(build_surface_for_scenario(
        "chapter-11-spine", incident, graph
    ).prompt)

    assert "retrieved_knowledge" not in current
    assert memory["retrieved_knowledge"][0]["source_run_id"] == "run-1042"
    assert "active_direction" not in memory
    assert spine["active_direction"]["allowed_tasks"] == ["inspect_pipeline_run"]


def test_spine_comparison_refuses_a_ready_choice_outside_direction():
    incident, graph = load_scenario("chapter-11-spine")
    receipt = DecisionReceipt(
        choice=ModelChoice(
            "inspect_replication_delay",
            "Measure whether delayed replication contributes to customer impact.",
            "replication delay from the discovered read endpoint",
        ),
        source="openai",
        model="recorded-model-id",
        elapsed_ms=250,
        observed_at="2026-07-20T12:00:00+00:00",
        instructions=CHOICE_INSTRUCTIONS,
        input_text=build_surface_for_scenario("chapter-11-spine", incident, graph).prompt,
        raw_output='{"task_id":"inspect_replication_delay"}',
    )

    record = build_record("chapter-11-spine", receipt, incident, graph)
    assert record["deterministic_result"]["kind"] == "direction"
    assert record["deterministic_result"]["status"] == "refused"
    assert "outside_active_milestone" in record["deterministic_result"]["reason"]

