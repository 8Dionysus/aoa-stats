# Continuity window

This part owns the bounded stats operation that makes one committed cross-owner
Continuity Window reference chain legible without taking continuity, memory,
playbook, or proof authority.

- status: `part_localized_with_public_contracts`
- stats source family: `read_models`
- source profile: `stats/read-models/active/continuity_window_summary.profile.json`
- local guide: `docs/CONTINUITY_WINDOW_SUMMARY.md`
- local example: `examples/continuity_window_summary.example.json`
- public schema: `schemas/continuity-window-summary.schema.json`
- committed reference output: `generated/continuity_window_summary.min.json`
- filesystem-free validation/projection:
  `src/aoa_stats_builder/continuity_window.py`
- committed-reference adapter:
  `src/aoa_stats_builder/continuity_window_sources.py`
- root compatibility facade: `scripts/build_views.py`
- live posture: reference-only until a canonical owner-runtime continuity
  artifact or receipt exists
- checks: `VALIDATION.md`
