# route-progression

Publishes the multi-axis route-progression read model.

This part aggregates admitted `progression_delta_receipt` events by route while
returning receipt and axis meaning to stronger owners.

- source profile:
  `stats/read-models/active/route_progression_summary.profile.json`
- vocabulary owner: `Agents-of-Abyss/mechanics/rpg`
- receipt owner: `aoa-skills` progression-delta contracts
- agent-layer axis owner:
  `aoa-agents/mechanics/rpg/parts/progression-model/`
- typed contract owner: `aoa-sdk` RPG models and checkpoint-carry contracts
- filesystem-free core: `src/aoa_stats_builder/route_progression.py`
- focused test:
  `mechanics/rpg/parts/route-progression/tests/test_route_progression.py`
- public schema: `schemas/route-progression-summary.schema.json`
- generated read model: `generated/route_progression_summary.min.json`
- root compatibility facade: `scripts/build_views.py`

The projection recognizes exactly `boundary_integrity`,
`execution_reliability`, `change_legibility`, `review_sharpness`,
`proof_discipline`, `provenance_hygiene`, and `deep_readiness`. Compatibility
details and the behavior-change stop-line are in `CONTRACT.md`. The committed
legacy numeric snapshot is reference-only; current semantic owner receipts are
not assigned numeric values.
