from __future__ import annotations

from orders_investigation.domain.incident import Evidence, EvidenceKey, Incident, opening_incident
from orders_investigation.graph.tasks import InvestigationGraph, opening_graph


def current_case() -> tuple[Incident, InvestigationGraph]:
    """Return the cumulative case after the migration job has been identified."""
    incident = opening_incident()
    graph = opening_graph()

    evidence_items = (
        (
            "inspect_connection_pool",
            Evidence(EvidenceKey.CONNECTION_POOL, "42 of 100 connections in use", "database_monitoring"),
        ),
        (
            "inspect_database_topology",
            Evidence(
                EvidenceKey.DATABASE_TOPOLOGY,
                "writer orders-db-w1; read replica orders-db-r1",
                "database_monitoring",
            ),
        ),
        (
            "inspect_writer_activity",
            Evidence(
                EvidenceKey.WRITER_ACTIVITY,
                "orders-search-backfill consumed most write capacity",
                "database_monitoring",
            ),
        ),
        (
            "inspect_migration_job",
            Evidence(
                EvidenceKey.MIGRATION_JOB,
                "orders-search-backfill started at 1:58 p.m.; source deploy-882",
                "migration_jobs",
            ),
        ),
    )
    for task_id, evidence in evidence_items:
        incident.record_evidence(evidence)
        graph.succeed(task_id, evidence)
    incident.revise_hypothesis(
        "A deployment-launched migration is consuming write capacity and delaying order completion.",
        based_on=(EvidenceKey.WRITER_ACTIVITY, EvidenceKey.MIGRATION_JOB),
    )
    return incident, graph
