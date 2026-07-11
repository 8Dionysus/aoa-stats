# AGENTS.md

## growth-cycle mechanic guidance

This package implements the stats-side projection of the common
`Agents-of-Abyss/mechanics/growth-cycle` mechanic.

Keep operation-specific docs, examples, supporting contracts, and focused
tests under the nearest part. Published catalog schemas and generated read
models may remain at repository root only when their stable public paths are
declared in `mechanics/topology.json`.

The three parts share deterministic receipt-to-read-model rules through
`src/aoa_stats_builder/growth_cycle.py`. Package-level tests are allowed only
for that shared core and its four authored read-model profiles; operation-
specific payload still belongs to the nearest part.

Start from the selected profile under `stats/read-models/active/` and the
`aoa-skills` event-kind registration before changing a projection. Keep the
root build facade responsible for input loading, output fan-out, and
check/write policy.

Stats outputs are descriptive and weaker than their named owner sources.
Do not add routing, proof, gate, or workflow authority here.
