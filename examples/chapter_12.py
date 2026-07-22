"""Chapter 12: lease takeover and fenced completion."""
import sqlite3
from orders_investigation.runtime.ownership import ClaimStore, StaleCompletion

store = ClaimStore(sqlite3.connect(":memory:"))
store.add_ready("inspect_pipeline_run")
first = store.claim("inspect_pipeline_run", "worker-a", now=100, lease_seconds=10)
second = store.claim("inspect_pipeline_run", "worker-b", now=111, lease_seconds=10)
print(f"FIRST OWNER             {first.worker_id} token={first.fencing_token}")
print(f"TAKEOVER                {second.worker_id} token={second.fencing_token}")
try:
    store.commit(first, "late result", now=112)
except StaleCompletion as error:
    print(f"LATE FIRST COMMIT       {error}")
store.commit(second, "deploy-882 launched migration", now=112)
print(f"CURRENT OWNER COMMITS   {store.state('inspect_pipeline_run')}")

