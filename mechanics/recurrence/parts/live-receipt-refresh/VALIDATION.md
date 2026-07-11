# Live receipt refresh validation

## Current focused checks

Run from the repository root:

```bash
python -m pytest -q \
  mechanics/recurrence/parts/live-receipt-refresh/tests/test_check_live_publishers.py \
  mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py \
  mechanics/recurrence/parts/live-receipt-refresh/tests/test_install_live_refresh_units.py
```

For a live workspace audit, separately run:

```bash
python scripts/check_live_publishers.py
```

The live audit depends on current owner-local receipt files and is not replaced
by fixture tests.

The focused refresh tests must also prove:

- the live allowlist is derived from active profiles with
  `live_state_capable: true`
- the authored live-admitted allowlist is exactly 20 while the cleanup universe
  still contains all 25 managed active read-model outputs
- reference-only Codex Plane Deployment, Continuity Window, Component Refresh,
  and Titan surfaces are absent from the live output and live catalog
- stale reference-only runtime files, including stale Codex Plane Deployment
  and Continuity Window copies, are removed rather than ignored
- live refresh passes an explicit Codex Plane `live` source mode and workspace
  root instead of allowing the committed example adapter to run

## CLI smoke

```bash
python scripts/check_live_publishers.py --help
python scripts/refresh_live_stats.py --help
python scripts/install_live_refresh_units.py --help
python scripts/validate_stats_source_home.py
python scripts/build_views.py --check
```

The tests prove that root compatibility commands load the part-local registry
and templates while preserving deterministic refresh behavior, authored
profile admission, live-only catalog membership, and stale-file cleanup.
