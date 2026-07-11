# Component refresh validation

Run from the repository root:

```bash
python -m pytest -q \
  mechanics/recurrence/parts/component-refresh/tests/test_component_refresh_summary.py \
  mechanics/recurrence/parts/component-refresh/tests/test_component_refresh_projection.py
python -m pytest -q tests/test_summary_surface_catalog.py tests/test_docs_routes.py
python -m pytest -q mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
```

The focused part test proves route discoverability, schema/example validity,
canonical owner-law refs, filesystem-free projection, and explicit reviewed
example adaptation. Root builder checks prove deterministic committed
publication. The live-refresh check proves the false-live profile is omitted
from local materialization and the live catalog while stale managed runtime
copies remain eligible for cleanup.
