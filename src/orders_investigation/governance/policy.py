from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PolicyFacts:
    service: str
    environment: str
    operation: str
    resource: str
    approval_status: str
    authorization_admitted: bool
    evidence_current: bool
    customer_impact_state: str


@dataclass(frozen=True)
class PolicyRule:
    rule_id: str
    required: tuple[tuple[str, object], ...]
    obligations: tuple[str, ...]


@dataclass(frozen=True)
class PolicyDecision:
    policy_version: str
    rule_id: str
    allow: bool
    reasons: tuple[str, ...]
    obligations: tuple[str, ...]


@dataclass(frozen=True)
class PolicySet:
    version: str
    rules: tuple[PolicyRule, ...]

    def __post_init__(self) -> None:
        identifiers = tuple(rule.rule_id for rule in self.rules)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("policy_rule_id_repeated")

    def decide(self, facts: PolicyFacts) -> PolicyDecision:
        values = asdict(facts)
        for rule in self.rules:
            mismatches = tuple(
                f"{field}_mismatch"
                for field, expected in rule.required
                if values[field] != expected
            )
            if not mismatches:
                return PolicyDecision(
                    policy_version=self.version,
                    rule_id=rule.rule_id,
                    allow=True,
                    reasons=(),
                    obligations=rule.obligations,
                )

        decisive = self.rules[0]
        reasons = tuple(
            f"{field}_mismatch"
            for field, expected in decisive.required
            if values[field] != expected
        )
        return PolicyDecision(
            policy_version=self.version,
            rule_id="default_deny",
            allow=False,
            reasons=reasons or ("no_allow_rule_matched",),
            obligations=(),
        )


def orders_report_policy() -> PolicySet:
    return PolicySet(
        version="orders-report-v1",
        rules=(
            PolicyRule(
                rule_id="publish_recovery_after_current_authorized_evidence",
                required=(
                    ("service", "orders"),
                    ("environment", "production"),
                    ("operation", "publish_recovery_update"),
                    ("resource", "orders-incident-report"),
                    ("approval_status", "approved"),
                    ("authorization_admitted", True),
                    ("evidence_current", True),
                    ("customer_impact_state", "recovered"),
                ),
                obligations=(
                    "attach_supporting_evidence",
                    "recheck_authorization_at_effect",
                    "record_policy_version",
                ),
            ),
        ),
    )

