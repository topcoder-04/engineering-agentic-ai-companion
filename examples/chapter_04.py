"""Show recorded evidence expanding the Chapter 4 task graph."""

from orders_investigation.domain.incident import Evidence, EvidenceKey
from orders_investigation.graph.tasks import opening_graph


def main() -> None:
    graph = opening_graph()
    graph.succeed(
        "inspect_database_topology",
        Evidence(
            EvidenceKey.DATABASE_TOPOLOGY,
            "writer=orders-db-w1; replica=orders-db-r1",
            "database_monitoring",
        ),
    )
    print("After topology:", ", ".join(graph.ready_ids()))

    graph.succeed(
        "inspect_writer_activity",
        Evidence(
            EvidenceKey.WRITER_ACTIVITY,
            "orders-search-backfill consumed most write capacity",
            "database_monitoring",
        ),
    )
    graph.succeed(
        "inspect_migration_job",
        Evidence(
            EvidenceKey.MIGRATION_JOB,
            "orders-search-backfill was launched by deploy-882",
            "migration_jobs",
        ),
    )
    print("After migration record:", ", ".join(graph.ready_ids()))


if __name__ == "__main__":
    main()

