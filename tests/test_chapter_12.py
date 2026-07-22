import sqlite3

import pytest

from orders_investigation.runtime.ownership import (
    ClaimStore,
    IntakeDeferred,
    StaleCompletion,
)


def test_expired_owner_cannot_commit_after_reclaim():
    store = ClaimStore(sqlite3.connect(":memory:"))
    store.add_ready("inspect_pipeline_run")
    first = store.claim("inspect_pipeline_run", "worker-a", now=100, lease_seconds=10)
    second = store.claim("inspect_pipeline_run", "worker-b", now=111, lease_seconds=10)

    assert second.fencing_token == first.fencing_token + 1
    with pytest.raises(StaleCompletion, match="claim_no_longer_current"):
        store.commit(first, "stale result", now=112)
    store.commit(second, "deploy-882 launched migration", now=112)
    assert store.state("inspect_pipeline_run") == (
        "succeeded", "worker-b", 2, "deploy-882 launched migration"
    )


def test_active_lease_prevents_second_claim():
    store = ClaimStore(sqlite3.connect(":memory:"))
    store.add_ready("inspect_pipeline_run")
    store.claim("inspect_pipeline_run", "worker-a", now=100, lease_seconds=10)
    with pytest.raises(ValueError, match="lease_active"):
        store.claim("inspect_pipeline_run", "worker-b", now=105, lease_seconds=10)


def test_in_flight_limit_defers_new_intake():
    store = ClaimStore(sqlite3.connect(":memory:"), max_in_flight=1)
    store.add_ready("inspect_pipeline_run")
    store.add_ready("inspect_replication_delay")
    store.claim("inspect_pipeline_run", "worker-a", now=100, lease_seconds=10)
    with pytest.raises(IntakeDeferred, match="in_flight_limit_reached"):
        store.claim("inspect_replication_delay", "worker-b", now=101, lease_seconds=10)

