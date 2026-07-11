# AGENTS.md

## rpg mechanic guidance

This package implements the stats-side projection of the common
`Agents-of-Abyss/mechanics/rpg` mechanic.

Keep operation-specific docs, examples, supporting contracts, and focused
tests under the nearest part. Published catalog schemas and generated read
models may remain at repository root only when their stable public paths are
declared in `mechanics/topology.json`.

Route Progression has one part-local deterministic core at
`src/aoa_stats_builder/route_progression.py` and one focused test route at
`mechanics/rpg/parts/route-progression/tests/test_route_progression.py`.
`scripts/build_views.py` retains compatibility aliases and repo-wide fan-out
only; new projection behavior belongs to the core.

Keep the owner chain explicit. The RPG center owns progression-reading
vocabulary and stop-lines, `aoa-skills` owns
`progression_delta_receipt` facts, `aoa-agents` owns the agent-layer seven-axis
overlay, and `aoa-sdk` owns typed progression and checkpoint-carry contracts.
aoa-stats remains weaker than every one of these owners.

This extraction preserves falsey `route_ref` fallback, Python integer
acceptance (including booleans), list-length caution counting, and latest
selection by `(observed_at, event_id)`. It rejects semantic-only
`axis_delta_summary` payloads instead of scoring them and normalizes an invalid
latest verdict to `unknown` for public-schema safety. The legacy numeric
projection is reference-only; changing its remaining compatibility behavior or
reopening live admission requires a separate owner-contract review.

Stats outputs are descriptive and weaker than their named owner sources.
Do not add routing, proof, gate, or workflow authority here.
