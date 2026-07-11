# Repeated window

This part owns the focused operation boundary for the deterministic
repeated-window summary without moving its stable public contract merely for
directory symmetry.

- status: `localized_active`
- stats source family: `read_models`
- source profile: `stats/read-models/active/repeated_window_summary.profile.json`
- public schema: `schemas/repeated-window-summary.schema.json`
- public output: `generated/repeated_window_summary.min.json`
- pure core: `src/aoa_stats_builder/repeated_window.py`
- root compatibility and fan-out: `scripts/build_views.py`
- focused tests: `tests/test_repeated_window.py`
- checks: `VALIDATION.md`

The part-local test suite is the operation payload. The schema and output
intentionally remain public, and the importable core remains in `src/` so the
root facade can reuse it without duplicating the projection.
