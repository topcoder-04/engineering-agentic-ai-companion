"""Run Chapter 3's bounded choice without provider credentials."""

from orders_investigation.domain.incident import opening_incident
from orders_investigation.decisions.model import FixedChoiceModel, ModelChoice
from orders_investigation.environment.requests import OPENING_OBSERVATION_REQUESTS


def main() -> None:
    incident = opening_incident()
    receipt = FixedChoiceModel(
        ModelChoice(
            "inspect_database_topology",
            "Find the database writer before interpreting pressure.",
            "writer and read-instance roles",
        )
    ).choose("opening decision surface")
    print(
        "Missing evidence:",
        ", ".join(key.value for key in incident.missing_evidence),
    )
    print("Declared choices:", ", ".join(sorted(OPENING_OBSERVATION_REQUESTS)))
    print("Model proposed:", receipt.choice.task_id)
    print("Deterministic runtime result: proposal recorded; no tool executed")


if __name__ == "__main__":
    main()

