from orders_investigation.platform.compatibility import CompatibilityWindow, migration_step
import pytest
from orders_investigation.runtime.journey import (
    orders_compatibility_window,
    run_compatible_orders_investigation,
)


def test_contract_migration_advances_readers_before_writers():
    window = CompatibilityWindow("trace/v1", "trace/v2", frozenset({"trace/v1", "trace/v2"}), "trace/v1")
    assert migration_step(window, {"trace/v1", "trace/v2"}) == "advance_readers_first"
    incompatible = CompatibilityWindow("trace/v1", "trace/v2", frozenset({"trace/v2"}), "trace/v2")
    assert migration_step(incompatible, {"trace/v1"}) == "hold_incompatible_reader"


def test_incompatible_reader_holds_orders_candidate_before_execution():
    accepted = run_compatible_orders_investigation(
        orders_compatibility_window(), frozenset({"trace/v2"})
    )
    assert accepted.registered.journey.completed is True

    with pytest.raises(
        ValueError,
        match="compatibility_refused:hold_incompatible_reader",
    ):
        run_compatible_orders_investigation(
            orders_compatibility_window(), frozenset({"trace/v0"})
        )
