import sqlite3

from orders_investigation.effects.idempotency import ReportEffectService, ResponseLost, report_update_intent

service = ReportEffectService(sqlite3.connect(":memory:"))
key = "report-update:run-1042:1"
try:
    service.apply(report_update_intent(), idempotency_key=key, lose_response=True)
except ResponseLost:
    print("First response lost after commit")
receipt = service.apply(report_update_intent(), idempotency_key=key)
print(f"Effects applied: {service.effect_count}")
print(f"Retry replayed: {receipt.replayed}")

