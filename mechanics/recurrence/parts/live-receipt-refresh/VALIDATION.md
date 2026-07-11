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

## CLI smoke

```bash
python scripts/check_live_publishers.py --help
python scripts/refresh_live_stats.py --help
python scripts/install_live_refresh_units.py --help
```

The tests prove that root compatibility commands load the part-local registry
and templates while preserving deterministic refresh behavior.
