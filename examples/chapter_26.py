"""Chapter 26: probe variations deliberately."""
from orders_investigation.operations.probes import variation_matrix

rows = variation_matrix(["small", "large"], ["none", "timeout"], [0, 500])
print("CHAPTER 26 — VARIATION MATRIX")
print("planned probes", len(rows), "stable first id", rows[0].variation_id)
