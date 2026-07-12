# Trusted Rollout History validation

Run from the repository root:

```bash
python -m pytest -q mechanics/release-support/parts/trusted-rollout-history/tests
python -m pytest -q mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q tests/test_build_views.py tests/test_summary_surface_catalog.py tests/test_docs_routes.py
```

These checks prove the four-file owner-history chain, filesystem-free core,
the strict-core versus legacy-facade lookup seam, stable public outputs,
false-live selectors, and managed stale cleanup.
