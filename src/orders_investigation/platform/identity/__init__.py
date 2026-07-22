"""Chapter 29: stable agent identity and immutable registration."""

from dataclasses import dataclass, field
from hashlib import sha256


def _digest(*values: str) -> str:
    return sha256("|".join(values).encode()).hexdigest()


@dataclass(frozen=True)
class AgentContract:
    agent_id: str
    version: str
    owner: str
    goal_schema: str
    trace_schema: str
    tool_contracts: tuple[str, ...]
    policy_bundle: str
    model_profile: str
    data_classes: frozenset[str]

    @property
    def manifest_digest(self) -> str:
        return _digest(
            self.agent_id, self.version, self.owner, self.goal_schema,
            self.trace_schema, *sorted(self.tool_contracts), self.policy_bundle,
            self.model_profile, *sorted(self.data_classes),
        )


@dataclass
class AgentRegistry:
    _contracts: dict[tuple[str, str], AgentContract] = field(default_factory=dict)
    _digests: dict[tuple[str, str], str] = field(default_factory=dict)

    def register(self, contract: AgentContract) -> str:
        key = (contract.agent_id, contract.version)
        digest = contract.manifest_digest
        if key in self._digests and self._digests[key] != digest:
            raise ValueError("immutable_version_conflict")
        self._contracts[key] = contract
        self._digests[key] = digest
        return digest

    def resolve(self, agent_id: str, version: str) -> AgentContract:
        try:
            return self._contracts[(agent_id, version)]
        except KeyError as exc:
            raise ValueError("agent_version_unknown") from exc
