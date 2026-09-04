# AGENTS.md

## Antifragility mechanic guide

This package implements the stats-side projection of the common
`Agents-of-Abyss/mechanics/antifragility` mechanic. Select the part from
`mechanics/topology.json`, then follow its contract, source profile, and
owner-local validation route as needed.

Keep operation-specific docs, examples, supporting contracts, and focused
tests under the nearest part. Published schemas and generated read models may
remain at root only where topology declares a stable public path.

Stats outputs are descriptive and weaker than named owner sources. Do not add
routing, proof, gate, workflow, live, or owner-acceptance authority here.

## Conditional validation

Use root `VALIDATION.md` for topology/source-home selection and the selected
part `VALIDATION.md` for exact negative and positive cases.
