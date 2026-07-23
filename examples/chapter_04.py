"""Show recorded evidence expanding the Chapter 4 task graph."""

from orders_investigation.domain.incident import Evidence, EvidenceKey
from orders_investigation.graph.tasks import opening_graph
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(4, description=__doc__)
    graph = opening_graph()
    demo.scenario(1, "Topology evidence reveals addressable resources")
    graph.succeed(
        "inspect_database_topology",
        Evidence(
            EvidenceKey.DATABASE_TOPOLOGY,
            "writer=orders-db-w1; replica=orders-db-r1",
            "database_monitoring",
        ),
    )
    demo.fields((("Ready after topology", ", ".join(graph.ready_ids())),))

    demo.scenario(2, "Writer and migration evidence reveal the launch mechanism")
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
    demo.fields((("Ready after migration record", ", ".join(graph.ready_ids())),))
    demo.notice(
        "Task identifiers appear only after recorded evidence makes their "
        "resources knowable. A failed observation would create no downstream work."
    )


if __name__ == "__main__":
    main()
