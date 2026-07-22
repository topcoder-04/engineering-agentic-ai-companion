import sqlite3

from orders_investigation.domain.incident import EvidenceKey, opening_incident
from orders_investigation.memory.store import (
    KnowledgeStore,
    RetrievalBudget,
    seed_dense_reviewed_knowledge,
    seed_missed_lesson_case,
    seed_reviewed_knowledge,
)


def test_retrieval_requires_reviewed_scope_and_current_gap():
    connection = sqlite3.connect(":memory:")
    store = KnowledgeStore(connection)
    seed_reviewed_knowledge(store)

    found = store.retrieve(
        service="orders-api",
        environment="orders-production",
        missing_evidence=("writer_activity",),
    )
    assert len(found) == 2
    assert {item.record.source_run_id for item in found} == {"run-1039", "run-1042"}
    assert {item.relevance for item in found} == {"scope_and_evidence_gap_match"}
    connection.close()


def test_other_environment_and_unrelated_gap_retrieve_nothing():
    connection = sqlite3.connect(":memory:")
    store = KnowledgeStore(connection)
    seed_reviewed_knowledge(store)
    assert store.retrieve(
        service="orders-api",
        environment="payments-production",
        missing_evidence=("writer_activity",),
    ) == ()
    assert store.retrieve(
        service="orders-api",
        environment="orders-production",
        missing_evidence=("dependency_health",),
    ) == ()
    connection.close()


def test_retrieved_knowledge_does_not_become_current_evidence():
    connection = sqlite3.connect(":memory:")
    store = KnowledgeStore(connection)
    seed_reviewed_knowledge(store)
    incident = opening_incident()
    before = incident.missing_evidence
    found = store.search(
        "migration",
        service=incident.service,
        environment=incident.environment,
        missing_evidence=tuple(key.value for key in incident.missing_evidence),
    )
    assert len(found) == 1
    assert EvidenceKey.WRITER_ACTIVITY not in incident.recorded_evidence
    assert incident.missing_evidence == before
    connection.close()


def test_dense_eligible_memory_is_bounded_and_omission_is_visible():
    connection = sqlite3.connect(":memory:")
    store = KnowledgeStore(connection)
    seed_dense_reviewed_knowledge(store, count=500)

    selection = store.select_for_surface(
        "deployment OR migration",
        service="orders-api",
        environment="orders-production",
        missing_evidence=("writer_activity",),
        budget=RetrievalBudget(max_records=3, max_bytes=700),
    )

    assert selection.eligible_count == 500
    assert selection.ranked_count == 500
    assert len(selection.selected) == 3
    assert selection.selected[0].record.source_run_id == "run-1042"
    assert selection.omitted_count == 497
    assert selection.limit_reason == "record_limit"
    assert selection.receipt.first_omitted_rank == 4
    assert selection.receipt.first_omitted_record_id == selection.receipt.ranked_record_ids[3]
    connection.close()


def test_surface_byte_limit_preserves_ranked_prefix_and_reports_omission():
    connection = sqlite3.connect(":memory:")
    store = KnowledgeStore(connection)
    seed_dense_reviewed_knowledge(store, count=5)

    selection = store.select_for_surface(
        "deployment OR migration",
        service="orders-api",
        environment="orders-production",
        missing_evidence=("writer_activity",),
        budget=RetrievalBudget(max_records=5, max_bytes=1),
    )

    assert selection.selected == ()
    assert selection.omitted_count == 5
    assert selection.used_bytes == 0
    assert selection.limit_reason == "byte_limit"
    connection.close()


def test_rank_four_lesson_is_visible_in_receipt_and_can_be_debugged():
    connection = sqlite3.connect(":memory:")
    store = KnowledgeStore(connection)
    record_ids = seed_missed_lesson_case(store)

    bounded = store.select_for_surface(
        "migration",
        service="orders-api",
        environment="orders-production",
        missing_evidence=("writer_activity",),
        budget=RetrievalBudget(max_records=3, max_bytes=2_000),
    )

    target = record_ids["useful_trigger_lesson"]
    assert bounded.receipt.ranked_record_ids[3] == target
    assert bounded.receipt.first_omitted_record_id == target
    assert bounded.receipt.first_omitted_rank == 4
    assert target not in bounded.receipt.selected_record_ids
    assert bounded.selected[-1].record.source_run_id == "run-general-3"

    expanded = store.select_for_surface(
        "migration",
        service="orders-api",
        environment="orders-production",
        missing_evidence=("writer_activity",),
        budget=RetrievalBudget(max_records=4, max_bytes=2_000),
    )
    assert expanded.receipt.ranked_record_ids == bounded.receipt.ranked_record_ids
    assert expanded.receipt.selected_record_ids[-1] == target

    focused = store.select_for_surface(
        "deployment OR trigger",
        service="orders-api",
        environment="orders-production",
        missing_evidence=("writer_activity",),
        budget=RetrievalBudget(max_records=3, max_bytes=2_000),
    )
    assert focused.receipt.ranked_record_ids == (target,)
    assert focused.receipt.selected_record_ids == (target,)
    assert focused.selected[0].record.source_evidence == (
        "writer_activity",
        "migration_job",
        "pipeline_trigger",
    )
    connection.close()
