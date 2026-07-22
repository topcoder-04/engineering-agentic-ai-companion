import json

from orders_investigation.runtime.boundary import ORDERS_BOUNDARY
from orders_investigation.context.surface import build_decision_surface
from orders_investigation.runtime.contracts.admission import admit
from orders_investigation.decisions.model import ModelChoice
from orders_investigation.environment.scenario import current_case


incident, graph = current_case()
surface = build_decision_surface(incident, graph)
choice = ModelChoice(
    "inspect_pipeline_run",
    "Inspect the recorded deployment that introduced the migration.",
    "the trigger and its configuration",
)
invocation = admit(choice, graph, ORDERS_BOUNDARY)

print(json.dumps(json.loads(surface.prompt), indent=2, sort_keys=True))
print(f"Admitted: {invocation.task_id} -> {invocation.source}/{invocation.resource}")

