import sqlite3

from orders_investigation.decisions.budget import (
    AttemptOutcome,
    DecisionBudget,
    DecisionLedger,
    ModelAttempt,
)
from orders_investigation.environment.scenario import current_case
from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.workflow import SQLiteRunStore


def main() -> None:
    demo = chapter_presentation(7, description=__doc__)
    connection = sqlite3.connect(":memory:")
    incident, graph = current_case()
    store = SQLiteRunStore(connection)
    ledger = DecisionLedger(DecisionBudget())
    ledger.record(ModelAttempt(AttemptOutcome.TIMEOUT, elapsed_ms=4_000))
    store.save("run-1042", incident, graph, ledger)
    restored_incident, restored_graph, restored_ledger = store.load_full("run-1042")

    demo.scenario(1, "The process resumes from one durable checkpoint")
    demo.fields(
        (
            ("Restored evidence records", len(restored_incident.recorded_evidence)),
            ("Restored ready work", ", ".join(restored_graph.ready_ids())),
            ("Restored decision attempts", len(restored_ledger.attempts)),
        ),
        style="evidence",
    )
    demo.state("Workflow checkpoint", True, "incident · graph · ledger restored together")
    demo.notice(
        "A restart does not reset the investigation's knowledge or its consumed "
        "decision budget. Recovery continues from durable facts."
    )


if __name__ == "__main__":
    main()
