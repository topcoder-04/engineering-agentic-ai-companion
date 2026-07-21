import sys

from orders_investigation.runtime.boundary import ORDERS_BOUNDARY, Request
from orders_investigation.domain.investigation import ReportUpdateResult
from orders_investigation.environment.opening_case import build_opening_case
from orders_investigation.environment.requests import OPENING_OBSERVATION_REQUESTS


def show(label: str, investigation) -> None:
    missing = ", ".join(sorted(key.value for key in investigation.missing_evidence)) or "none"
    print(label)
    print(f"hypothesis                 {investigation.current_hypothesis}")
    print(f"recorded evidence          {', '.join(sorted(key.value for key in investigation.evidence))}")
    print(f"missing evidence           {missing}")
    print(f"report saved               {investigation.report_saved}")
    print(f"investigation complete     {investigation.investigation_complete}")


def main() -> None:
    chapter = sys.argv[1] if len(sys.argv) > 1 else "chapter-01"
    if chapter == "chapter-02":
        decisions = {
            "topology": OPENING_OBSERVATION_REQUESTS["inspect_database_topology"],
            "payments metrics": Request(
                "observe", "service_metrics", "payments-production", "payments-api", "latency"
            ),
            "Orders rollback": Request(
                "rollback", "deployment_pipeline", "orders-production", "orders-release", "latest"
            ),
            "incident report": Request(
                "update_report", "incident_record", "orders-production", "incident_report", "save"
            ),
        }
        print("BOUNDARY DECISIONS")
        for label, request in decisions.items():
            result = "permitted" if ORDERS_BOUNDARY.allows(request) else "rejected before outside work"
            print(f"{label:<24} {result}")
        print("\nThe boundary answers whether work may happen. It does not rank the permitted requests.")
        return
    if chapter != "chapter-01":
        raise SystemExit(f"This checkpoint supports chapter-01 or chapter-02, not {chapter!r}.")

    investigation = build_opening_case()
    show("OPENING CASE", investigation)
    investigation.report_update_result = ReportUpdateResult.ACCEPTED
    print()
    show("REPORT UPDATE SUCCEEDS, EVIDENCE STILL MISSING", investigation)


if __name__ == "__main__":
    main()
