from orders_investigation.graph.spine import SpineTransitionRefused, orders_spine

spine = orders_spine()
spine.advance("writer_activity")
spine.advance("migration_job")
print(f"Question: {spine.current.question}")
print(f"Allowed: {', '.join(spine.current.allowed_tasks)}")
try:
    spine.admit_task("inspect_replication_delay")
except SpineTransitionRefused as error:
    print(f"Refused: {error}")

