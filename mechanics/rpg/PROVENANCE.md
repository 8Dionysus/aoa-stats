# rpg provenance

The common mechanic vocabulary comes from
`Agents-of-Abyss/mechanics/rpg`.

The payload in this package was regrouped from aoa-stats root districts by
operation, preserving content and stable public publication paths. Route
Progression aggregation moved from `scripts/build_views.py` to
`src/aoa_stats_builder/route_progression.py`; the historical root names remain
compatibility aliases and repo-wide fan-out only.

The input chain remains source-owned: the RPG center owns
progression-reading vocabulary and stop-lines, `aoa-skills` publishes
progression-delta receipts, `aoa-agents/mechanics/rpg/parts/progression-model/`
owns the agent-layer seven-axis overlay, and `aoa-sdk` owns typed progression
and checkpoint-carry contracts. aoa-stats owns only the bounded read-model
question and committed compatibility projection.

The extraction intentionally preserves the former builder's compatibility
behavior for route fallback, Python integer acceptance, caution list length,
and latest-event selection. Semantic-only owner receipts are rejected rather
than mapped to scores, and invalid verdicts normalize to `unknown` so successful
outputs remain schema-valid. The legacy numeric projection is reference-only
until an owner-approved semantic projection contract exists.

The topology records current localized and retained public routes only;
former root placement remains recoverable from Git rename history.
