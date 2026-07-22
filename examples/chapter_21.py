"""Chapter 21: execute and refuse the same Orders report-write path."""

from orders_investigation.runtime.journey import run_orders_investigation


def main() -> None:
    accepted = run_orders_investigation()
    refused = run_orders_investigation(evidence_current=False)
    print("CHAPTER 21 — EFFECT-TIME ENFORCEMENT")
    print("accepted", accepted.completed, "report version", accepted.report_version)
    print("stale evidence", refused.refusal, "report version", refused.report_version)


if __name__ == "__main__":
    main()
