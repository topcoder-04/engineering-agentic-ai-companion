import pytest

from orders_investigation.domain.incident import Evidence, EvidenceKey, opening_incident
from orders_investigation.graph.tasks import TaskStatus, opening_graph


def test_topology_result_expands_the_graph() -> None:
    graph = opening_graph()
    assert "inspect_writer_activity" not in graph.tasks

    graph.succeed(
        "inspect_database_topology",
        Evidence(
            EvidenceKey.DATABASE_TOPOLOGY,
            "writer=orders-db-w1; replica=orders-db-r1",
            "database_monitoring",
        ),
    )

    assert graph.tasks["inspect_database_topology"].status == TaskStatus.SUCCEEDED
    assert {"inspect_writer_activity", "inspect_replication_delay"} <= set(graph.ready_ids())


def test_failed_topology_does_not_create_endpoint_work() -> None:
    graph = opening_graph()
    graph.fail("inspect_database_topology")

    assert graph.tasks["inspect_database_topology"].status == TaskStatus.FAILED
    assert "inspect_writer_activity" not in graph.tasks
    assert "inspect_replication_delay" not in graph.tasks


def test_evidence_reaches_job_and_pipeline_systems() -> None:
    graph = opening_graph()
    graph.succeed(
        "inspect_database_topology",
        Evidence(EvidenceKey.DATABASE_TOPOLOGY, "roles", "database_monitoring"),
    )
    graph.succeed(
        "inspect_writer_activity",
        Evidence(EvidenceKey.WRITER_ACTIVITY, "orders-search-backfill", "database_monitoring"),
    )
    assert "inspect_migration_job" in graph.ready_ids()

    graph.succeed(
        "inspect_migration_job",
        Evidence(EvidenceKey.MIGRATION_JOB, "started by deploy-882", "migration_jobs"),
    )
    assert "inspect_pipeline_run" in graph.ready_ids()


def test_hypothesis_revision_names_its_recorded_support() -> None:
    incident = opening_incident()
    incident.record_evidence(Evidence(
        EvidenceKey.WRITER_ACTIVITY,
        "orders-search-backfill consumed most write capacity",
        "database_monitoring",
    ))
    incident.record_evidence(Evidence(
        EvidenceKey.MIGRATION_JOB,
        "orders-search-backfill was launched by deploy-882",
        "migration_jobs",
    ))
    previous = incident.hypothesis

    incident.revise_hypothesis(
        "A deployment-launched migration is consuming write capacity.",
        based_on=(EvidenceKey.WRITER_ACTIVITY, EvidenceKey.MIGRATION_JOB),
    )

    revision = incident.hypothesis_revisions[-1]
    assert revision.previous == previous
    assert revision.current == incident.hypothesis
    assert revision.based_on == (EvidenceKey.WRITER_ACTIVITY, EvidenceKey.MIGRATION_JOB)


def test_hypothesis_cannot_claim_unrecorded_evidence() -> None:
    incident = opening_incident()
    with pytest.raises(ValueError, match="supporting_evidence_not_recorded"):
        incident.revise_hypothesis(
            "A deployment launched the workload.",
            based_on=(EvidenceKey.MIGRATION_JOB,),
        )

