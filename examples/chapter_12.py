"""Chapter 12: lease takeover and fenced completion."""
import sqlite3

from orders_investigation.presentation import chapter_presentation
from orders_investigation.runtime.ownership import ClaimStore, StaleCompletion


def main() -> None:
    demo = chapter_presentation(12, description=__doc__)
    store = ClaimStore(sqlite3.connect(":memory:"))
    store.add_ready("inspect_pipeline_run")
    first = store.claim("inspect_pipeline_run", "worker-a", now=100, lease_seconds=10)
    second = store.claim("inspect_pipeline_run", "worker-b", now=111, lease_seconds=10)

    demo.scenario(1, "An expired lease is taken over")
    demo.fields(
        (
            ("First owner", f"{first.worker_id} · token {first.fencing_token}"),
            ("Takeover owner", f"{second.worker_id} · token {second.fencing_token}"),
        ),
        style="evidence",
    )
    demo.scenario(2, "The stale owner returns after takeover")
    try:
        store.commit(first, "late result", now=112)
    except StaleCompletion as error:
        demo.decision(False, refused_label="STALE COMMIT REFUSED", reason=str(error))
    store.commit(second, "deploy-882 launched migration", now=112)
    demo.execution(True, f"current owner committed {store.state('inspect_pipeline_run')}")
    demo.notice(
        "Lease expiry enables recovery; the higher fencing token prevents the "
        "former owner from committing after ownership changed."
    )


if __name__ == "__main__":
    main()
