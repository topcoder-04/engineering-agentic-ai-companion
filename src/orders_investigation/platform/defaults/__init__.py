"""Chapter 33: safe-by-default project scaffolding."""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ScaffoldRequest:
    agent_id: str
    owner: str
    capability_id: str


@dataclass(frozen=True)
class Scaffold:
    files: Mapping[str, str]
    declared_exceptions: tuple[str, ...] = ()


def scaffold(request: ScaffoldRequest, overrides: Mapping[str, str] | None = None) -> Scaffold:
    files = {
        "agent.yaml": f"agent_id: {request.agent_id}\nowner: {request.owner}\ncapability: {request.capability_id}\n",
        "tests/test_conformance.py": "def test_platform_conformance():\n    assert True\n",
        "runbook.md": f"# {request.agent_id} operating runbook\n",
    }
    exceptions: list[str] = []
    for path, value in (overrides or {}).items():
        files[path] = value
        exceptions.append(f"override:{path}")
    return Scaffold(files, tuple(sorted(exceptions)))


def admit_scaffold(
    project: Scaffold,
    *,
    approved_exceptions: tuple[str, ...] = (),
) -> tuple[str, ...]:
    """Require the paved-path files and explicit approval for every escape hatch."""
    required = {"agent.yaml", "tests/test_conformance.py", "runbook.md"}
    reasons = [
        f"required_file_missing:{path}" for path in sorted(required - set(project.files))
    ]
    approved = set(approved_exceptions)
    reasons.extend(
        f"exception_not_approved:{item}"
        for item in project.declared_exceptions
        if item not in approved
    )
    return tuple(reasons)
