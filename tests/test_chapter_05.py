import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from orders_investigation.runtime.boundary import ORDERS_BOUNDARY
from orders_investigation.context.surface import build_decision_surface
from orders_investigation.runtime.contracts.admission import Proposal, admit
from orders_investigation.domain.incident import Evidence, EvidenceKey
from orders_investigation.decisions.model import ModelChoice, OpenAIChoiceModel
from orders_investigation.environment.scenario import current_case


def test_decision_surface_matches_cumulative_state():
    incident, graph = current_case()
    payload = json.loads(build_decision_surface(incident, graph).prompt)
    assert payload["missing_evidence"] == ["pipeline_trigger"]
    assert payload["ready_tasks"] == [
        "inspect_database_error_rate",
        "inspect_dependency_health",
        "inspect_pipeline_run",
        "inspect_replication_delay",
    ]
    assert "prior_model_reason" not in payload


def test_unsupported_reason_can_pass_admission_without_becoming_evidence():
    incident, graph = current_case()
    choice = ModelChoice(
        "inspect_pipeline_run",
        "deploy-882 probably increased migration parallelism.",
        "a worker-count or batch-size change",
    )
    invocation = admit(choice, graph, ORDERS_BOUNDARY)
    assert invocation.task_id == "inspect_pipeline_run"
    incident.record_evidence(Evidence(
        EvidenceKey.PIPELINE_TRIGGER,
        "deploy-882 launched orders-search-backfill; worker count remained 4",
        "deployment_pipeline",
    ))
    assert "parallelism" not in incident.recorded_evidence[EvidenceKey.PIPELINE_TRIGGER].value
    assert choice.reason not in {item.value for item in incident.recorded_evidence.values()}


def test_stale_completed_topology_is_refused_by_current_graph():
    _, graph = current_case()
    with pytest.raises(ValueError, match="task_not_ready"):
        admit(ModelChoice(
            "inspect_database_topology",
            "Inspect topology again.",
            "writer and read replica",
        ), graph, ORDERS_BOUNDARY)


def test_malformed_and_unknown_choices_fail_closed():
    _, graph = current_case()
    with pytest.raises(ValidationError):
        Proposal.model_validate({"task_id": "inspect_pipeline_run", "reason": "Find trigger."})
    with pytest.raises(ValueError, match="unknown_task"):
        admit(ModelChoice("cancel_migration", "Stop pressure.", "job stopped"), graph, ORDERS_BOUNDARY)


def test_fixed_receipt_preserves_application_supplied_request_and_raw_output():
    from orders_investigation.decisions.model import FixedChoiceModel

    choice = ModelChoice("inspect_pipeline_run", "Find its trigger.", "deployment record")
    receipt = FixedChoiceModel(choice).choose('{"ready_tasks":["inspect_pipeline_run"]}')
    assert receipt.instructions is not None
    assert receipt.input_text == '{"ready_tasks":["inspect_pipeline_run"]}'
    assert receipt.raw_output is not None
    assert receipt.observed_at is None


def test_openai_adapter_requests_and_consumes_the_proposal_schema():
    class FakeResponses:
        def __init__(self):
            self.request = None

        def parse(self, **kwargs):
            self.request = kwargs
            return SimpleNamespace(
                output_parsed=Proposal(
                    task_id="inspect_pipeline_run",
                    reason="Inspect the deployment record named by the migration job.",
                    expected_evidence="The trigger and its recorded configuration.",
                ),
                output_text=(
                    '{"task_id":"inspect_pipeline_run",'
                    '"reason":"Inspect the deployment record named by the migration job.",'
                    '"expected_evidence":"The trigger and its recorded configuration."}'
                ),
                usage=SimpleNamespace(input_tokens=120, output_tokens=28),
                id="resp_structured",
            )

    responses = FakeResponses()
    adapter = OpenAIChoiceModel.__new__(OpenAIChoiceModel)
    adapter.client = SimpleNamespace(responses=responses)
    adapter.model = "recorded-model-id"

    receipt = adapter.choose('{"ready_tasks":["inspect_pipeline_run"]}')

    assert responses.request["text_format"] is Proposal
    assert receipt.choice.task_id == "inspect_pipeline_run"
    assert receipt.response_id == "resp_structured"
    assert receipt.input_units == 120
    assert receipt.output_units == 28

