import sys

from .domain.investigation import ReportUpdateResult
from .environment.opening_case import build_opening_case


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
    if chapter != "chapter-01":
        raise SystemExit(f"This checkpoint supports chapter-01, not {chapter!r}.")

    investigation = build_opening_case()
    show("OPENING CASE", investigation)
    investigation.report_update_result = ReportUpdateResult.ACCEPTED
    print()
    show("REPORT UPDATE SUCCEEDS, EVIDENCE STILL MISSING", investigation)


if __name__ == "__main__":
    main()
