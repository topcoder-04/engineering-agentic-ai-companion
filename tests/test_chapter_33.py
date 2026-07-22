from orders_investigation.platform.defaults import ScaffoldRequest, scaffold


def test_scaffold_supplies_safe_contract_test_and_runbook():
    result = scaffold(ScaffoldRequest("search-agent", "search-oncall", "read-only"))
    assert set(result.files) == {"agent.yaml", "tests/test_conformance.py", "runbook.md"}
    assert result.declared_exceptions == ()


def test_scaffold_makes_override_visible():
    result = scaffold(ScaffoldRequest("a", "o", "c"), {"custom/router.py": "# owned"})
    assert result.declared_exceptions == ("override:custom/router.py",)
