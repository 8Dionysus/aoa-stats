# AGENTS.md

## checkpoint mechanic guidance

This package implements the stats-side projection of the common
`Agents-of-Abyss/mechanics/checkpoint` mechanic.

Keep operation-specific docs, examples, supporting contracts, and focused
tests under the nearest part. Published catalog schemas and generated read
models may remain at repository root only when their stable public paths are
declared in `mechanics/topology.json`.

Stats outputs are descriptive and weaker than their named owner sources.
Do not add routing, proof, gate, or workflow authority here.

Runtime Closeout has one deterministic core at
`src/aoa_stats_builder/runtime_closeout.py` and focused proof under
`parts/runtime-closeout/tests/`. Preserve the historical wave-receipt
projection as a compatibility snapshot. The Checkpoint center owns closeout
law; `abyss-stack` owns runtime trial production and gate truth; `aoa-sdk`
owns reviewed-closeout transport. Do not alias the current trial or return
receipt kinds into the historical wave kind without a cross-owner ABI change.
