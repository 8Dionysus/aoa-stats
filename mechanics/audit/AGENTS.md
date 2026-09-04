# AGENTS.md

## Audit mechanic guide

This package implements the stats-side projection of the common
`Agents-of-Abyss/mechanics/audit` mechanic. Select the operation through
`mechanics/topology.json` and its source profile or operation record.

## Core ownership

- `core_skill_observation.py` is shared only by the core-skill-application and
  surface-strength-detection parts; its cross-part proof remains in the Audit
  package test district.
- `object_observation.py` serves only object-observation; its focused proof
  remains under that part.
- Source-coverage and drift-review logic have distinct source and adapter
  boundaries and must not be merged into either core.
- `scripts/build_views.py` is the root compatibility/build facade; new
  filesystem-free projection logic belongs in the appropriate part core.

Registered live receipts remain source-owned evidence. Audit may consume the
active supersession-resolved set and publish bounded observations, but it must
not redefine receipt admission, owner success, source health, surface
authority, or validation sufficiency.

Preserve the existing ordered-input compatibility contracts: surface detection
keeps missing context in the legacy `activated` bucket and supplied-order
window bounds; object observation reports input-first, temporal-latest, and
input-last family verdicts. These are compatibility rules, not owner truth.

## Conditional validation and closeout

Open the selected part contract. For `core-skill-application` or
`surface-strength-detection`, use the package [`VALIDATION.md`](VALIDATION.md)
for their shared deterministic core; otherwise use the selected part
`VALIDATION.md`. Report source inputs, ordered-input behavior, generated parity,
and the boundary that remains outside descriptive Audit output. Do not add
routing, proof, gate, or workflow authority.
