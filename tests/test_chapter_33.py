import pytest
from orders_investigation.platform.defaults import ScaffoldRequest, admit_scaffold, scaffold
from orders_investigation.runtime.journey import run_scaffolded_orders_investigation


def test_scaffold_supplies_safe_contract_test_and_runbook():
    result = scaffold(ScaffoldRequest("search-agent", "search-oncall", "read-only"))
    assert set(result.files) == {"agent.yaml", "tests/test_conformance.py", "runbook.md"}
    assert result.declared_exceptions == ()


def test_scaffold_makes_override_visible():
    result = scaffold(ScaffoldRequest("a", "o", "c"), {"custom/router.py": "# owned"})
    assert result.declared_exceptions == ("override:custom/router.py",)


def test_scaffold_admission_requires_approval_for_every_override():
    result = scaffold(ScaffoldRequest("a", "o", "c"), {"custom/router.py": "# owned"})
    assert admit_scaffold(result) == (
        "exception_not_approved:override:custom/router.py",
    )
    assert admit_scaffold(
        result, approved_exceptions=("override:custom/router.py",)
    ) == ()


def test_orders_paved_path_runs_but_unapproved_override_cannot_launch_work():
    assert run_scaffolded_orders_investigation().registered.journey.completed is True
    with pytest.raises(
        ValueError,
        match="scaffold_refused:exception_not_approved:override:custom/router.py",
    ):
        run_scaffolded_orders_investigation(overrides={"custom/router.py": "# owned"})
