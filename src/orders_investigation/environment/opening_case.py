from orders_investigation.domain.evidence import Evidence, EvidenceKey
from orders_investigation.domain.investigation import Investigation


def build_opening_case() -> Investigation:
    investigation = Investigation(
        goal="Explain the order timeouts with recorded evidence and save the incident report.",
        current_hypothesis="Pressure in the database path is delaying order completion.",
    )
    for item in (
        Evidence(EvidenceKey.SERVICE_TIMEOUTS, "18 percent", "service metrics"),
        Evidence(EvidenceKey.DATABASE_WRITE_LATENCY, "4.8 seconds", "database monitoring"),
        Evidence(EvidenceKey.APPLICATION_CPU, "within normal range", "service metrics"),
    ):
        investigation.record(item)
    return investigation

