# core-skill-application

Publishes the bounded core-skill application read model.

This part observes finish-stage core-skill application receipts without
claiming that a skill, kernel, or owner workflow succeeded.

- source profile:
  `stats/read-models/active/core_skill_application_summary.profile.json`
- shared filesystem-free core:
  `src/aoa_stats_builder/core_skill_observation.py`
- focused shared test:
  `mechanics/audit/tests/test_core_skill_observation.py`
- public schema: `schemas/core-skill-application-summary.schema.json`
- generated read model: `generated/core_skill_application_summary.min.json`
- root compatibility facade: `scripts/build_views.py`

The package-level core and test are shared only with
`surface-strength-detection`. Stable public paths remain at root because the
stats source manifest and external consumers depend on them.
