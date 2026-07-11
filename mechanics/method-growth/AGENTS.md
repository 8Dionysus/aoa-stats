# AGENTS.md

## method-growth mechanic guidance

This package implements the stats-side projection of the common
`Agents-of-Abyss/mechanics/method-growth` mechanic.

Keep operation-specific docs, examples, supporting contracts, and focused
tests under the nearest part. Published catalog schemas and generated read
models may remain at repository root only when their stable public paths are
declared in `mechanics/topology.json`.

The deterministic core remains shared because Supersession Pruning consumes
normalized Candidate Lineage and landing receipts. Behavioral proof does not:
each surviving builder owns its schema, ordering, non-mutation, stability, and
non-inference checks under the nearest part-local `tests/` district. Add a
package-level test only for a future invariant that genuinely cannot be owned
by either part.

Stats outputs are descriptive and weaker than their named owner sources.
Do not add routing, proof, gate, or workflow authority here.
