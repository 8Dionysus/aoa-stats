# trusted-rollout-history

Projects two bounded summaries from the checked-in trusted rollout history
owned by `8Dionysus`. This part is neither the deploy-local Codex Plane route
nor the cadence-example route.

- source profiles:
  `stats/read-models/active/codex_rollout_operations_summary.profile.json` and
  `stats/read-models/active/codex_rollout_drift_summary.profile.json`
- guide: `docs/TRUSTED_ROLLOUT_HISTORY_SUMMARIES.md`
- public schemas: `schemas/codex-rollout-operations-summary.schema.json` and
  `schemas/codex-rollout-drift-summary.schema.json`
- committed outputs: `generated/codex_rollout_operations_summary.min.json` and
  `generated/codex_rollout_drift_summary.min.json`
- filesystem-free core: `src/aoa_stats_builder/codex_trusted_rollout.py`
- checked-in-history adapter:
  `src/aoa_stats_builder/codex_trusted_rollout_sources.py`
- root compatibility facade: `scripts/build_views.py`
- focused proof: `tests/test_codex_trusted_rollout_projection.py`

The two localized examples mirror the stable public output shape. They are
examples of derived history projections, not runtime evidence.
