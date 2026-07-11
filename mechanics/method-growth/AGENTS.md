# AGENTS.md

## method-growth mechanic guidance

This package implements the stats-side projection of the common
`Agents-of-Abyss/mechanics/method-growth` mechanic.

Keep operation-specific docs, examples, supporting contracts, and focused
tests under the nearest part. Published catalog schemas and generated read
models may remain at repository root only when their stable public paths are
declared in `mechanics/topology.json`.

Package-level tests are allowed only for deterministic core shared by more
than one Method Growth part; operation-specific payload still belongs to the
nearest part.

Stats outputs are descriptive and weaker than their named owner sources.
Do not add routing, proof, gate, or workflow authority here.
