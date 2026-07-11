# rollout-campaign

Projects bounded campaign cadence from a committed three-example owner chain.

This part owns its operation route and the localized payload roots declared in
`mechanics/topology.json`. Its stats source family owns the bounded meaning;
public schemas and generated outputs stay at their declared publication paths
when consumers depend on those paths.

- source profile:
  `stats/read-models/active/rollout_campaign_summary.profile.json`
- guide: `docs/ROLLOUT_CAMPAIGN_SUMMARY.md`
- public schema: `schemas/rollout-campaign-summary.schema.json`
- committed output: `generated/rollout_campaign_summary.min.json`
- shared filesystem-free cadence core:
  `src/aoa_stats_builder/rollout_cadence.py`
- committed-example adapter: `src/aoa_stats_builder/rollout_cadence_sources.py`
- root compatibility facade: `scripts/build_views.py`
- focused proof: `tests/test_rollout_campaign_projection.py`

This part owns the campaign projection. The audit sibling
`drift-shadow-review` owns the review projection over the same validated input
bundle.
