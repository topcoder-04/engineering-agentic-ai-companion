import sqlite3

from orders_investigation.effects.idempotency import ReportEffectService, ResponseLost, report_update_intent
from orders_investigation.presentation import chapter_presentation


def main() -> None:
    demo = chapter_presentation(8, description=__doc__)
    service = ReportEffectService(sqlite3.connect(":memory:"))
    key = "report-update:run-1042:1"
    response_lost = False
    try:
        service.apply(report_update_intent(), idempotency_key=key, lose_response=True)
    except ResponseLost:
        response_lost = True
    receipt = service.apply(report_update_intent(), idempotency_key=key)

    demo.scenario(1, "The first response is lost after commit")
    demo.fields(
        (
            ("Stable idempotency key", key),
            ("Caller observed response", "NO" if response_lost else "YES"),
        ),
        style="evidence",
    )
    demo.scenario(2, "The same logical attempt is retried")
    demo.fields(
        (
            ("Effects applied", service.effect_count),
            ("Effect id", receipt.effect_id),
            ("Stored status", receipt.status),
            ("Retry replayed receipt", receipt.replayed),
        )
    )
    demo.execution(service.effect_count == 1, "report update applied exactly once")
    demo.notice(
        "The stable key identifies the logical effect, so transport uncertainty "
        "can replay the receipt without repeating the write."
    )


if __name__ == "__main__":
    main()
