"""Run Chapter 3's bounded choice without provider credentials."""

from orders_investigation.domain.incident import Evidence, EvidenceKey, opening_incident
from orders_investigation.decisions.model import FixedChoiceModel, ModelChoice
from orders_investigation.environment.requests import OPENING_OBSERVATION_REQUESTS
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(3, description=__doc__)
    incident = opening_incident()
    first = FixedChoiceModel(
        ModelChoice(
            "inspect_connection_pool",
            "Check whether connection exhaustion explains the delay.",
            "pool use",
        )
    ).choose("opening decision surface")
    missing_before = incident.missing_evidence
    incident.record_evidence(
        Evidence(
            EvidenceKey.CONNECTION_POOL,
            "42 of 100 connections in use",
            "database_monitoring",
        )
    )
    second = FixedChoiceModel(
        ModelChoice(
            "inspect_database_topology",
            "Find the database writer before interpreting pressure.",
            "writer and read-instance roles",
        )
    ).choose("opening decision surface")
    demo.scenario(1, "A permitted choice does not close the current gap")
    demo.fields(
        (
            ("Missing evidence", ", ".join(key.value for key in missing_before)),
            ("Declared choices", ", ".join(sorted(OPENING_OBSERVATION_REQUESTS))),
            ("Model choice", first.choice.task_id),
            ("Observed result", "connection pool 42 of 100"),
            (
                "Evidence gaps closed",
                len(missing_before) - len(incident.missing_evidence),
            ),
        ),
        style="evidence",
    )
    demo.decision(True, approved_label="DECLARED OBSERVATION ADMITTED")
    demo.scenario(2, "The next choice follows the remaining evidence gap")
    demo.fields((("Next useful choice", second.choice.task_id),))
    demo.notice(
        "The model records a bounded recommendation. Only the declared "
        "observation result becomes evidence, and permitted does not mean useful."
    )


if __name__ == "__main__":
    main()
