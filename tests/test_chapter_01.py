from orders_investigation import Evidence, EvidenceKey, ReportUpdateResult
from orders_investigation.environment.opening_case import build_opening_case


def record_missing_evidence(investigation) -> None:
    investigation.record(Evidence(EvidenceKey.WRITER_ACTIVITY, "high write load", "database monitoring"))
    investigation.record(Evidence(EvidenceKey.MIGRATION_JOB, "orders backfill", "migration records"))
    investigation.record(Evidence(EvidenceKey.PIPELINE_TRIGGER, "deployment 884", "deployment records"))


def test_opening_case_preserves_the_three_real_evidence_gaps() -> None:
    investigation = build_opening_case()

    assert investigation.missing_evidence == {
        EvidenceKey.WRITER_ACTIVITY,
        EvidenceKey.MIGRATION_JOB,
        EvidenceKey.PIPELINE_TRIGGER,
    }
    assert not investigation.investigation_complete


def test_complete_evidence_does_not_hide_an_unsuccessful_report_result() -> None:
    investigation = build_opening_case()
    record_missing_evidence(investigation)

    assert not investigation.missing_evidence
    assert not investigation.investigation_complete


def test_saved_report_does_not_hide_missing_evidence() -> None:
    investigation = build_opening_case()
    investigation.report_update_result = ReportUpdateResult.ACCEPTED

    assert not investigation.investigation_complete


def test_completion_requires_evidence_and_observed_report_result() -> None:
    investigation = build_opening_case()
    record_missing_evidence(investigation)
    investigation.report_update_result = ReportUpdateResult.ACCEPTED

    assert investigation.investigation_complete

    del investigation.evidence[EvidenceKey.PIPELINE_TRIGGER]
    assert not investigation.investigation_complete
