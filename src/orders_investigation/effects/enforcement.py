from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from orders_investigation.governance.policy import PolicyDecision, PolicyFacts, PolicySet


class GuardrailRefused(ValueError):
    pass


@dataclass(frozen=True)
class EffectContext:
    facts: PolicyFacts
    authorized_intent_digest: str


@dataclass(frozen=True)
class EffectCommand:
    effect_id: str
    operation: str
    resource: str
    content: str
    intent_digest: str
    expected_resource_version: int
    policy_decision: PolicyDecision | None
    applied_obligations: tuple[str, ...]
    supporting_evidence: tuple[str, ...]


@dataclass(frozen=True)
class EnforcementReceipt:
    effect_id: str
    resource: str
    previous_resource_version: int
    current_resource_version: int
    policy_version: str
    rule_id: str
    applied_obligations: tuple[str, ...]


class EnforcedReportStore:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS policy_activation ("
            "slot INTEGER PRIMARY KEY CHECK(slot = 1), version TEXT NOT NULL)"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS enforced_reports ("
            "resource TEXT PRIMARY KEY, version INTEGER NOT NULL, content TEXT NOT NULL)"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS enforced_effects ("
            "effect_id TEXT PRIMARY KEY, resource TEXT NOT NULL, "
            "previous_version INTEGER NOT NULL, current_version INTEGER NOT NULL, "
            "policy_version TEXT NOT NULL, rule_id TEXT NOT NULL, "
            "intent_digest TEXT NOT NULL, obligations TEXT NOT NULL)"
        )

    def seed_report(self, resource: str, version: int, content: str) -> None:
        self.connection.execute(
            "INSERT INTO enforced_reports(resource, version, content) VALUES(?, ?, ?)",
            (resource, version, content),
        )
        self.connection.commit()

    def activate_policy(self, version: str) -> None:
        if not version:
            raise GuardrailRefused("policy_version_empty")
        self.connection.execute(
            "INSERT INTO policy_activation(slot, version) VALUES(1, ?) "
            "ON CONFLICT(slot) DO UPDATE SET version = excluded.version",
            (version,),
        )
        self.connection.commit()

    def active_policy(self) -> str:
        row = self.connection.execute(
            "SELECT version FROM policy_activation WHERE slot = 1"
        ).fetchone()
        if row is None:
            raise GuardrailRefused("policy_not_activated")
        return row[0]

    def report(self, resource: str) -> tuple[int, str]:
        row = self.connection.execute(
            "SELECT version, content FROM enforced_reports WHERE resource = ?",
            (resource,),
        ).fetchone()
        if row is None:
            raise KeyError(resource)
        return row[0], row[1]

    def apply(
        self,
        command: EffectCommand,
        context: EffectContext,
        policy: PolicySet,
    ) -> EnforcementReceipt:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            if command.policy_decision is None:
                raise GuardrailRefused("policy_decision_missing")
            active_version = self.active_policy()
            if policy.version != active_version:
                raise GuardrailRefused("policy_runtime_not_active")
            if command.policy_decision.policy_version != active_version:
                raise GuardrailRefused("policy_decision_not_active")
            if command.operation != context.facts.operation:
                raise GuardrailRefused("effect_operation_changed")
            if command.resource != context.facts.resource:
                raise GuardrailRefused("effect_resource_changed")
            if command.intent_digest != context.authorized_intent_digest:
                raise GuardrailRefused("effect_intent_changed")

            current = policy.decide(context.facts)
            if not current.allow:
                reason = current.reasons[0] if current.reasons else "default_deny"
                raise GuardrailRefused(f"current_policy_denied:{reason}")
            if command.policy_decision != current:
                raise GuardrailRefused("policy_decision_stale")

            applied = set(command.applied_obligations)
            for obligation in current.obligations:
                if obligation not in applied:
                    raise GuardrailRefused(f"obligation_not_applied:{obligation}")
            if not command.supporting_evidence:
                raise GuardrailRefused("supporting_evidence_missing")

            row = self.connection.execute(
                "SELECT version FROM enforced_reports WHERE resource = ?",
                (command.resource,),
            ).fetchone()
            if row is None:
                raise GuardrailRefused("effect_resource_unknown")
            previous_version = row[0]
            if previous_version != command.expected_resource_version:
                raise GuardrailRefused("resource_version_changed")

            update = self.connection.execute(
                "UPDATE enforced_reports SET version = version + 1, content = ? "
                "WHERE resource = ? AND version = ?",
                (command.content, command.resource, command.expected_resource_version),
            )
            if update.rowcount != 1:
                raise GuardrailRefused("resource_version_changed")
            current_version = previous_version + 1
            self.connection.execute(
                "INSERT INTO enforced_effects(effect_id, resource, previous_version, "
                "current_version, policy_version, rule_id, intent_digest, obligations) "
                "VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    command.effect_id,
                    command.resource,
                    previous_version,
                    current_version,
                    current.policy_version,
                    current.rule_id,
                    command.intent_digest,
                    ",".join(sorted(applied)),
                ),
            )
            self.connection.commit()
            return EnforcementReceipt(
                command.effect_id,
                command.resource,
                previous_version,
                current_version,
                current.policy_version,
                current.rule_id,
                tuple(sorted(applied)),
            )
        except Exception:
            self.connection.rollback()
            raise

