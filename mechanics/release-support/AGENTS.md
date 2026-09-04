# AGENTS.md

## Release Support mechanic guide

This package implements the stats-side projection of the common
`Agents-of-Abyss/mechanics/release-support` mechanic. Select the target through
the source profile or operation record and `mechanics/topology.json`.

Keep operation-specific docs, examples, supporting contracts, and focused
tests under the nearest part. Published schemas and generated read models may
remain at root only where topology declares a stable public route.

Stats outputs are descriptive and weaker than named owner sources. Do not add
routing, proof, gate, workflow, release-admission, or owner-acceptance
authority.

## Conditional validation

Use the selected part `VALIDATION.md` for exact procedure and root
`VALIDATION.md` for cross-route or release-readiness selection. Publication,
CI, review, merge, and post-landing claims remain with `docs/RELEASING.md` and
the observed platform surfaces.
