# AGENTS.md

## Growth Cycle mechanic guide

This package implements the stats-side projection of the common
`Agents-of-Abyss/mechanics/growth-cycle` mechanic. Select a profile, event kind,
and part through the authored source and topology routes before editing.

The parts share deterministic receipt-to-read-model rules through
`src/aoa_stats_builder/growth_cycle.py`. Package-level proof is limited to that
shared core and its authored profiles; operation-specific payload remains with
the nearest part. The root build facade owns input loading, output fan-out,
and check/write policy.

Stats outputs are descriptive and weaker than named owner sources. Do not add
routing, proof, gate, workflow, or owner-acceptance authority.

## Conditional validation

Open the selected part `VALIDATION.md` and use root `VALIDATION.md` for a
cross-route or generated-parity check. Report receipt posture, shared-core
coverage, and missing owner evidence.
