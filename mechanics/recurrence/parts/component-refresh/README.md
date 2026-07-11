# Component refresh

This part owns the bounded stats operation that projects one committed
Component Refresh reference snapshot without becoming current refresh truth.

- status: `part_localized_with_public_contracts`
- stats source family: `read_models`
- source profile: `stats/read-models/active/component_refresh_summary.profile.json`
- local guide: `docs/COMPONENT_REFRESH_SUMMARIES.md`
- local examples: `examples/`
- public schema: `schemas/component-refresh-summary.schema.json`
- committed reference output: `generated/component_refresh_summary.min.json`
- filesystem-free core: `src/aoa_stats_builder/component_refresh.py`
- reviewed-example adapter: `src/aoa_stats_builder/component_refresh_sources.py`
- compatibility facade: `scripts/build_views.py`
- live posture: `live_state_capable: false`
- decision: `docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`
- checks: `VALIDATION.md`

The public schema and committed generated snapshot remain at stable root
consumer routes. The adapter loads reviewed `aoa-sdk` examples only for that
reference build; local live refresh must not replay them under
`state/generated/`. The operation guide, owner-law examples, and focused tests
are canonical here.
