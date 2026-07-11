# surface-strength-detection

Exposes advisory detection signals without routing authority.

This part projects advisory detection fields from finish-stage core-skill
application receipts without assigning surface authority.

- source profile:
  `stats/read-models/active/surface_detection_summary.profile.json`
- shared filesystem-free core:
  `src/aoa_stats_builder/core_skill_observation.py`
- focused shared test:
  `mechanics/audit/tests/test_core_skill_observation.py`
- public schema: `schemas/surface-detection-summary.schema.json`
- generated read model: `generated/surface_detection_summary.min.json`
- root compatibility facade: `scripts/build_views.py`

The package-level core and test are shared only with
`core-skill-application`. For byte compatibility, missing, non-mapping, or
empty detection context is retained in the legacy `activated` bucket. That
bucket is a projection label only: it is not an owner-authored activation
claim. Candidate counts and date-window bounds likewise retain the ordered
legacy behavior detailed in `CONTRACT.md`.
