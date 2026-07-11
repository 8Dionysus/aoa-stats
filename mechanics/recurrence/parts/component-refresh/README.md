# Component refresh

This part owns the bounded stats operation that describes recurring component
refresh posture without becoming refresh truth.

- status: `part_localized_with_public_contracts`
- stats source family: `read_models`
- source profile: `stats/read-models/active/component_refresh_summary.profile.json`
- local guide: `docs/COMPONENT_REFRESH_SUMMARIES.md`
- local examples: `examples/`
- public schema: `schemas/component-refresh-summary.schema.json`
- public output: `generated/component_refresh_summary.min.json`
- shared builder: `scripts/build_views.py`
- checks: `VALIDATION.md`

The public schema and generated summary remain at stable root consumer routes;
the operation guide, owner-law examples, and focused test are canonical here.
