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
- the authored live-admitted allowlist is exactly 11 while the cleanup universe
  still contains all 23 active outputs plus the retired Owner Landing and Titan
  Summon output names
- the 12 reference-only active profiles, including Route Progression,
  Runtime Closeout, Memory Movement, Stress Recovery, trusted rollout-history,
  and both cadence projections, are absent from the live output and live catalog
- the retired Owner Landing and Titan Summon builders and catalog entries stay
  absent while their tombstones remove any stale runtime copies
- stale reference-only runtime files, including all three newly closed
  selectors and all four audited rollout and cadence companions, are removed
  on non-empty and empty receipt paths
- a real current owner source without a refresh observation route, as with the
  reviewed memory corpus, remains insufficient for live admission
- live refresh passes an explicit Codex Plane `live` source mode and workspace
  root instead of allowing the committed example adapter to run
- live refresh does not invoke the Route Progression compatibility builder
  against semantic-only current owner receipts
- live refresh does not read the historical runtime-wave log or invoke the
  Runtime Closeout compatibility builder against current owner receipts

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
