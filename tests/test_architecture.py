"""The repository tree is a reader-facing architecture contract."""

from pathlib import Path


SOURCE = Path(__file__).parents[1] / "src" / "orders_investigation"


def test_final_responsibility_packages_are_present():
    required = {
        "domain", "environment", "decisions", "graph", "runtime", "context",
        "effects", "memory", "integrations", "coordination", "governance",
        "evaluation", "operations", "platform",
    }
    assert required <= {path.name for path in SOURCE.iterdir() if path.is_dir()}


def test_platform_subdomains_make_the_part_five_map_visible():
    required = {
        "identity", "capabilities", "authority", "placement", "defaults",
        "releases", "lifecycle", "compatibility", "risk",
    }
    platform = SOURCE / "platform"
    assert required <= {path.name for path in platform.iterdir() if path.is_dir()}


def test_generic_code_buckets_are_forbidden():
    forbidden = {"utils", "helpers", "misc"}
    assert not [path for path in SOURCE.rglob("*") if path.is_dir() and path.name in forbidden]


def test_old_flat_responsibility_modules_do_not_return():
    allowed = {"__init__.py", "demo.py", "live_demo.py"}
    assert {path.name for path in SOURCE.glob("*.py")} <= allowed
