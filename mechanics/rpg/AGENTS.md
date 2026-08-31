# AGENTS.md

## RPG mechanic guide

This package implements the stats-side projection of the common
`Agents-of-Abyss/mechanics/rpg` mechanic. Select the route-progression profile
and part through the source record and topology.

Route Progression has one part-local deterministic core at
`src/aoa_stats_builder/route_progression.py` and one focused test route in the
part. `scripts/build_views.py` retains compatibility aliases and root fan-out;
new projection behavior belongs in the core.

The RPG center owns progression-reading vocabulary and stop-lines,
`aoa-skills` owns `progression_delta_receipt` facts, `aoa-agents` owns the
agent-layer seven-axis overlay, and `aoa-sdk` owns typed progression and
checkpoint-carry contracts. `aoa-stats` remains weaker than each owner.

Preserve falsey `route_ref` fallback, Python integer acceptance including
booleans, list-length caution counting, latest selection by
`(observed_at, event_id)`, rejection of semantic-only `axis_delta_summary`, and
normalization of an invalid latest verdict to `unknown`. The legacy numeric
projection is reference-only; reopening live admission requires owner review.

## Conditional validation and closeout

Use the route-progression part `VALIDATION.md` and root `VALIDATION.md` for
cross-route checks. Report compatibility behavior, owner refs, generated
parity, and the fact that output does not prove rank, mastery, unlock,
navigation, or owner progression truth.
