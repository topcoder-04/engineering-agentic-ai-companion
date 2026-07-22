from orders_investigation.platform.compatibility import CompatibilityWindow, migration_step


def test_contract_migration_advances_readers_before_writers():
    window = CompatibilityWindow("trace/v1", "trace/v2", frozenset({"trace/v1", "trace/v2"}), "trace/v1")
    assert migration_step(window, {"trace/v1", "trace/v2"}) == "advance_readers_first"
    incompatible = CompatibilityWindow("trace/v1", "trace/v2", frozenset({"trace/v2"}), "trace/v2")
    assert migration_step(incompatible, {"trace/v1"}) == "hold_incompatible_reader"
