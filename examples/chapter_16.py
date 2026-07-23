"""Replace future work while preserving completed commitments."""

import sqlite3

from orders_investigation.graph.planning import (
    Commitment,
    CommitmentStatus,
    EvidenceReference,
    Plan,
    PlanRefused,
    PlanStore,
)
from orders_investigation.presentation import chapter_presentation

def main() -> None:
    demo = chapter_presentation(16, description=__doc__)
    first = Plan(
        "orders-run",
        1,
        "How should migration pressure be reduced?",
        (
            EvidenceReference("migration_status", "running"),
            EvidenceReference("writer_pressure", "high"),
        ),
        (
            Commitment("inspect_pipeline_run", CommitmentStatus.SUCCEEDED),
            Commitment("inspect_migration_controls", CommitmentStatus.READY),
            Commitment("propose_throttle_action", CommitmentStatus.WAITING),
        ),
    )
    replacement = Plan(
        "orders-run",
        2,
        "Did Orders recover after the migration completed?",
        (
            EvidenceReference("migration_status", "completed"),
            EvidenceReference("writer_pressure", "falling"),
        ),
        (
            Commitment("inspect_pipeline_run", CommitmentStatus.SUCCEEDED),
            Commitment("confirm_writer_recovery", CommitmentStatus.READY),
            Commitment("confirm_order_recovery", CommitmentStatus.READY),
        ),
        supersedes_version=1,
    )
    store = PlanStore(sqlite3.connect(":memory:"))
    store.create(first, {"migration_status": "running", "writer_pressure": "high"})
    receipt = store.replace(
        replacement,
        {"migration_status": "completed", "writer_pressure": "falling"},
    )
    demo.scenario(1, "Recovery evidence replaces only future work")
    demo.fields(
        (
            ("Preserved succeeded", ", ".join(receipt.preserved_succeeded)),
            ("Superseded future", ", ".join(receipt.superseded_future)),
            ("Added future", ", ".join(receipt.added_future)),
            ("Current plan version", replacement.version),
        ),
        style="evidence",
    )
    try:
        store.require_current("orders-run", 1)
    except PlanRefused as error:
        demo.decision(False, refused_label="LATE PLAN REFUSED", reason=str(error))
    demo.notice(
        "New evidence may replace unfinished commitments. Succeeded work remains "
        "part of history, and a late worker cannot act on the superseded version."
    )


if __name__ == "__main__":
    main()
