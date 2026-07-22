"""Chapter 28: route only to an exact healthy fleet cell."""
from orders_investigation.operations.fleet import Cell, FleetRequest, route

cells = (Cell("full", "us", "v2", "p3", 1, 1, True, "canary"), Cell("ready", "us", "v2", "p3", 4, 1, True, "canary"))
decision = route(cells, FleetRequest("r-28", "us", "v2", "p3", "canary"))
print("CHAPTER 28 — FLEET ROUTING")
print("selected cell", decision.cell_id, "refusals", decision.reasons)
