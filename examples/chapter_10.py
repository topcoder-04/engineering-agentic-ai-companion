import sqlite3

from orders_investigation.memory.store import KnowledgeStore, RetrievalBudget, seed_dense_reviewed_knowledge
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(10, description=__doc__)
    store = KnowledgeStore(sqlite3.connect(":memory:"))
    seed_dense_reviewed_knowledge(store, count=500)
    selection = store.select_for_surface(
        "deployment OR migration",
        service="orders-api",
        environment="orders-production",
        missing_evidence=("writer_activity",),
        budget=RetrievalBudget(max_records=3, max_bytes=700),
    )
    demo.scenario(1, "Reviewed knowledge is scoped before it is ranked")
    demo.fields(
        (
            ("Eligible after safety scope", selection.eligible_count),
            ("Included", len(selection.selected)),
            ("Omitted", selection.omitted_count),
            ("Selection limit", selection.limit_reason),
            ("Current evidence gaps closed", 0),
        ),
        style="evidence",
    )
    demo.decision(True, approved_label="BOUNDED CONTEXT SELECTED")
    demo.notice(
        "Omitted records stay omitted rather than being replaced by shorter, "
        "lower-ranked text. Retrieved knowledge guides judgment but closes no "
        "current evidence gap."
    )


if __name__ == "__main__":
    main()
