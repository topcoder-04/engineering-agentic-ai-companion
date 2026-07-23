from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeRecord:
    service: str
    environment: str
    evidence_gap: str
    finding: str
    source_run_id: str
    source_evidence: tuple[str, ...]
    reviewed: bool


@dataclass(frozen=True)
class RetrievedKnowledge:
    record_id: int
    record: KnowledgeRecord
    relevance: str


@dataclass(frozen=True)
class RetrievalBudget:
    max_records: int
    max_bytes: int

    def __post_init__(self) -> None:
        if self.max_records < 1:
            raise ValueError("max_records_must_be_positive")
        if self.max_bytes < 1:
            raise ValueError("max_bytes_must_be_positive")


@dataclass(frozen=True)
class RetrievalSelection:
    selected: tuple[RetrievedKnowledge, ...]
    eligible_count: int
    ranked_count: int
    omitted_count: int
    used_bytes: int
    limit_reason: str | None
    receipt: "RetrievalReceipt"


@dataclass(frozen=True)
class RetrievalReceipt:
    query: str
    eligible_record_ids: tuple[int, ...]
    ranked_record_ids: tuple[int, ...]
    selected_record_ids: tuple[int, ...]
    first_omitted_record_id: int | None
    first_omitted_rank: int | None
    limit_reason: str | None


class KnowledgeStore:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS knowledge_records ("
            "record_id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "service TEXT NOT NULL, "
            "environment TEXT NOT NULL, "
            "evidence_gap TEXT NOT NULL, "
            "finding TEXT NOT NULL, "
            "source_run_id TEXT NOT NULL, "
            "source_evidence TEXT NOT NULL, "
            "reviewed INTEGER NOT NULL"
            ")"
        )
        self.connection.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts "
            "USING fts5(record_id UNINDEXED, finding)"
        )
        self.connection.commit()

    def add(self, record: KnowledgeRecord) -> int:
        cursor = self.connection.execute(
            "INSERT INTO knowledge_records("
            "service, environment, evidence_gap, finding, source_run_id, "
            "source_evidence, reviewed"
            ") VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                record.service,
                record.environment,
                record.evidence_gap,
                record.finding,
                record.source_run_id,
                ",".join(record.source_evidence),
                int(record.reviewed),
            ),
        )
        record_id = int(cursor.lastrowid)
        self.connection.execute(
            "INSERT INTO knowledge_fts(record_id, finding) VALUES (?, ?)",
            (record_id, record.finding),
        )
        self.connection.commit()
        return record_id

    def retrieve(
        self,
        *,
        service: str,
        environment: str,
        missing_evidence: tuple[str, ...],
    ) -> tuple[RetrievedKnowledge, ...]:
        if not missing_evidence:
            return ()
        placeholders = ",".join("?" for _ in missing_evidence)
        rows = self.connection.execute(
            "SELECT record_id, service, environment, evidence_gap, finding, "
            "source_run_id, source_evidence, reviewed "
            "FROM knowledge_records "
            "WHERE reviewed = 1 AND service = ? AND environment = ? "
            f"AND evidence_gap IN ({placeholders}) "
            "ORDER BY record_id",
            (service, environment, *missing_evidence),
        ).fetchall()
        return tuple(self._retrieved(row, "scope_and_evidence_gap_match") for row in rows)

    def search(
        self,
        query: str,
        *,
        service: str,
        environment: str,
        missing_evidence: tuple[str, ...],
    ) -> tuple[RetrievedKnowledge, ...]:
        candidates = {
            item.record_id: item
            for item in self.retrieve(
                service=service,
                environment=environment,
                missing_evidence=missing_evidence,
            )
        }
        if not candidates or not query.strip():
            return tuple(candidates.values())
        rows = self.connection.execute(
            "SELECT CAST(record_id AS INTEGER), bm25(knowledge_fts) "
            "FROM knowledge_fts WHERE knowledge_fts MATCH ? ORDER BY 2, 1",
            (query,),
        ).fetchall()
        return tuple(
            RetrievedKnowledge(
                record_id,
                candidates[record_id].record,
                "scope_gap_and_text_match",
            )
            for record_id, _ in rows
            if record_id in candidates
        )

    def select_for_surface(
        self,
        query: str,
        *,
        service: str,
        environment: str,
        missing_evidence: tuple[str, ...],
        budget: RetrievalBudget,
    ) -> RetrievalSelection:
        eligible = self.retrieve(
            service=service,
            environment=environment,
            missing_evidence=missing_evidence,
        )
        ranked = self.search(
            query,
            service=service,
            environment=environment,
            missing_evidence=missing_evidence,
        )
        selected: list[RetrievedKnowledge] = []
        used_bytes = 0
        limit_reason: str | None = None

        for item in ranked:
            if len(selected) >= budget.max_records:
                limit_reason = "record_limit"
                break
            item_bytes = len(self._surface_json(item).encode("utf-8"))
            if used_bytes + item_bytes > budget.max_bytes:
                limit_reason = "byte_limit"
                break
            selected.append(item)
            used_bytes += item_bytes

        first_omitted = ranked[len(selected)] if len(selected) < len(ranked) else None
        receipt = RetrievalReceipt(
            query=query,
            eligible_record_ids=tuple(item.record_id for item in eligible),
            ranked_record_ids=tuple(item.record_id for item in ranked),
            selected_record_ids=tuple(item.record_id for item in selected),
            first_omitted_record_id=first_omitted.record_id if first_omitted else None,
            first_omitted_rank=len(selected) + 1 if first_omitted else None,
            limit_reason=limit_reason,
        )
        return RetrievalSelection(
            selected=tuple(selected),
            eligible_count=len(eligible),
            ranked_count=len(ranked),
            omitted_count=len(ranked) - len(selected),
            used_bytes=used_bytes,
            limit_reason=limit_reason,
            receipt=receipt,
        )

    @staticmethod
    def _surface_json(item: RetrievedKnowledge) -> str:
        return json.dumps(
            {
                "finding": item.record.finding,
                "source_run_id": item.record.source_run_id,
                "relevant_to": item.record.evidence_gap,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @staticmethod
    def _retrieved(row: tuple[object, ...], relevance: str) -> RetrievedKnowledge:
        (
            record_id,
            service,
            environment,
            evidence_gap,
            finding,
            source_run_id,
            source_evidence,
            reviewed,
        ) = row
        return RetrievedKnowledge(
            int(record_id),
            KnowledgeRecord(
                str(service),
                str(environment),
                str(evidence_gap),
                str(finding),
                str(source_run_id),
                tuple(filter(None, str(source_evidence).split(","))),
                bool(reviewed),
            ),
            relevance,
        )


def seed_reviewed_knowledge(store: KnowledgeStore) -> None:
    store.add(KnowledgeRecord(
        service="orders-api",
        environment="orders-production",
        evidence_gap="writer_activity",
        finding=(
            "A deployment-launched migration consumed writer capacity. "
            "Topology and writer activity identified the workload before its job record."
        ),
        source_run_id="run-1042",
        source_evidence=("database_topology", "writer_activity", "migration_job"),
        reviewed=True,
    ))
    store.add(KnowledgeRecord(
        service="orders-api",
        environment="orders-staging",
        evidence_gap="writer_activity",
        finding="A staging load test created elevated writer activity.",
        source_run_id="run-staging-12",
        source_evidence=("writer_activity",),
        reviewed=True,
    ))
    store.add(KnowledgeRecord(
        service="orders-api",
        environment="orders-production",
        evidence_gap="writer_activity",
        finding=(
            "A long-running transaction held writer capacity. "
            "Writer activity and transaction age identified the competing work."
        ),
        source_run_id="run-1039",
        source_evidence=("writer_activity",),
        reviewed=True,
    ))
    store.add(KnowledgeRecord(
        service="orders-api",
        environment="orders-production",
        evidence_gap="writer_activity",
        finding="Connection settings probably caused the writer delay.",
        source_run_id="run-1031",
        source_evidence=(),
        reviewed=False,
    ))


def seed_dense_reviewed_knowledge(store: KnowledgeStore, count: int = 500) -> None:
    if count < 1:
        raise ValueError("count_must_be_positive")
    store.add(KnowledgeRecord(
        service="orders-api",
        environment="orders-production",
        evidence_gap="writer_activity",
        finding=(
            "A deployment-launched migration consumed writer capacity. "
            "Topology and writer activity identified the workload before its job record."
        ),
        source_run_id="run-1042",
        source_evidence=("database_topology", "writer_activity", "migration_job"),
        reviewed=True,
    ))
    for index in range(1, count):
        store.add(KnowledgeRecord(
            service="orders-api",
            environment="orders-production",
            evidence_gap="writer_activity",
            finding=(
                f"Reviewed migration pattern {index:03d} associated writer activity "
                "with a previously identified workload."
            ),
            source_run_id=f"run-memory-{index:03d}",
            source_evidence=("writer_activity",),
            reviewed=True,
        ))


def seed_missed_lesson_case(store: KnowledgeStore) -> dict[str, int]:
    record_ids: dict[str, int] = {}
    for index in range(1, 4):
        record_ids[f"selected_{index}"] = store.add(KnowledgeRecord(
            service="orders-api",
            environment="orders-production",
            evidence_gap="writer_activity",
            finding=(
                f"Migration migration pattern {index} associated writer activity "
                "with a previously identified workload."
            ),
            source_run_id=f"run-general-{index}",
            source_evidence=("writer_activity",),
            reviewed=True,
        ))
    record_ids["useful_trigger_lesson"] = store.add(KnowledgeRecord(
        service="orders-api",
        environment="orders-production",
        evidence_gap="writer_activity",
        finding=(
            "A deployment trigger launched the migration workload. "
            "Inspect the release record after writer activity names the job."
        ),
        source_run_id="run-reviewed-trigger",
        source_evidence=("writer_activity", "migration_job", "pipeline_trigger"),
        reviewed=True,
    ))
    return record_ids

