import sqlite3

from orders_investigation.memory.store import KnowledgeStore, RetrievalBudget, seed_dense_reviewed_knowledge

store = KnowledgeStore(sqlite3.connect(":memory:"))
seed_dense_reviewed_knowledge(store, count=5)
selection = store.select_for_surface(
    "deployment OR migration",
    service="orders-api",
    environment="orders-production",
    missing_evidence=("writer_activity",),
    budget=RetrievalBudget(max_records=1, max_bytes=700),
)
print(f"Eligible: {selection.eligible_count}")
print(f"Included: {len(selection.selected)}")
print(f"Omitted: {selection.omitted_count}")
print(f"Limit: {selection.limit_reason}")
