from dataclasses import dataclass, field
from enum import StrEnum

from orders_investigation.domain.evidence import Evidence, EvidenceKey


class ReportUpdateResult(StrEnum):
    NOT_ATTEMPTED = "not_attempted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


REQUIRED_EVIDENCE = frozenset(EvidenceKey)


@dataclass
class Investigation:
    goal: str
    current_hypothesis: str
    evidence: dict[EvidenceKey, Evidence] = field(default_factory=dict)
    report_update_result: ReportUpdateResult = ReportUpdateResult.NOT_ATTEMPTED

    def record(self, item: Evidence) -> None:
        self.evidence[item.key] = item

    @property
    def missing_evidence(self) -> frozenset[EvidenceKey]:
        return REQUIRED_EVIDENCE.difference(self.evidence)

    @property
    def report_saved(self) -> bool:
        return self.report_update_result is ReportUpdateResult.ACCEPTED

    @property
    def investigation_complete(self) -> bool:
        return not self.missing_evidence and self.report_saved

