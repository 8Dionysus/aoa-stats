# Consumer regrounding validation

## Current focused checks

Run from the repository root:

```bash
python scripts/build_views.py --check
python -m pytest -q \
  mechanics/boundary-bridge/parts/consumer-regrounding/tests/test_consumer_regrounding_signals.py \
  tests/test_summary_surface_catalog.py
```

These checks constrain catalog shape, owner-truth references, authority
ceilings, intake-coverage flags, and committed generated parity.

The topology validator additionally proves that the focused test is part-local
and only declared public/compatibility routes remain at root.
