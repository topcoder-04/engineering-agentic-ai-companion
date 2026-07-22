import sqlite3

from orders_investigation.decisions.budget import DecisionBudget, DecisionLedger
from orders_investigation.environment.scenario import current_case
from orders_investigation.runtime.workflow import SQLiteRunStore

connection = sqlite3.connect(":memory:")
incident, graph = current_case()
store = SQLiteRunStore(connection)
store.save("run-1042", incident, graph, DecisionLedger(DecisionBudget()))
restored_incident, restored_graph, restored_ledger = store.load_full("run-1042")
print(f"Restored evidence: {len(restored_incident.recorded_evidence)}")
print(f"Ready work: {', '.join(restored_graph.ready_ids())}")
print(f"Decision attempts: {len(restored_ledger.attempts)}")

