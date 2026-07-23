from orders_investigation.domain.incident import (
    Evidence,
    EvidenceKey,
    opening_incident,
)
from orders_investigation.environment.requests import OPENING_OBSERVATION_REQUESTS
from orders_investigation.live_demo import (
    build_failure_record,
    build_record,
    load_scenario,
)
from orders_investigation.decisions.model import (
    CHOICE_INSTRUCTIONS,
    DecisionReceipt,
    FixedChoiceModel,
    ModelChoice,
    build_model_request,
)


def test_weak_result_can_precede_a_more_useful_choice():
    incident = opening_incident()
    missing_before = incident.missing_evidence
    weak = FixedChoiceModel(
        ModelChoice("inspect_connection_pool", "Check exhaustion.", "pool use")
    ).choose("opening")
    assert weak.choice.task_id == "inspect_connection_pool"
    incident.record_evidence(
        Evidence(
            EvidenceKey.CONNECTION_POOL,
            "42 of 100",
            "database_monitoring",
        )
    )
    assert incident.missing_evidence == missing_before
    useful = FixedChoiceModel(
        ModelChoice(
            "inspect_database_topology",
            "Find the writer.",
            "writer roles",
        )
    ).choose("updated")
    assert useful.choice.task_id == "inspect_database_topology"


def test_instructions_bound_choice_without_claiming_execution():
    request = build_model_request(
        '{"ready_tasks":["inspect_database_topology"]}'
    )
    assert request.instructions == CHOICE_INSTRUCTIONS
    assert "Use only a task_id listed in ready_tasks" in request.instructions
    assert "Do not describe an action as completed" in request.instructions


def test_chapter_three_has_declared_choices_but_no_task_graph():
    incident, observations = load_scenario("chapter-03")
    assert tuple(sorted(observations)) == tuple(
        sorted(OPENING_OBSERVATION_REQUESTS)
    )
    assert EvidenceKey.DATABASE_TOPOLOGY not in incident.recorded_evidence


def test_live_record_preserves_choice_and_boundary_result():
    incident, observations = load_scenario("chapter-03")
    receipt = DecisionReceipt(
        ModelChoice(
            "inspect_database_topology",
            "Find writer.",
            "roles",
        ),
        "openai",
        "recorded-model-id",
        250,
        observed_at="2026-07-20T12:00:00+00:00",
        instructions=CHOICE_INSTRUCTIONS,
        input_text="surface",
        raw_output='{"task_id":"inspect_database_topology"}',
        response_id="recorded",
    )
    record = build_record(
        "chapter-03",
        receipt,
        incident,
        observations,
    )
    assert record["deterministic_result"]["status"] == "permitted"
    assert record["deterministic_result"]["request"]["resource"] == "orders-db"


def test_provider_failure_does_not_invent_a_choice():
    class QuotaFailure(Exception):
        status_code = 429
        request_id = "request-quota"
        body = {
            "code": "insufficient_quota",
            "message": "quota unavailable",
        }

    incident, observations = load_scenario("chapter-03")
    record = build_failure_record(
        "chapter-03",
        "recorded-model-id",
        incident,
        observations,
        QuotaFailure(),
        observed_at="2026-07-20T12:00:00+00:00",
        elapsed_ms=180,
    )
    assert record["failure"]["code"] == "insufficient_quota"
    assert record["choice"] is None
