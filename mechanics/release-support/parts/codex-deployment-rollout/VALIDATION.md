# Codex Plane Deployment validation

Run from the repository root:

```bash
python -m pytest -q mechanics/release-support/parts/codex-deployment-rollout/tests
python -m pytest -q mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q tests/test_build_views.py tests/test_summary_surface_catalog.py tests/test_docs_routes.py
```

These checks prove the reference chain is coherent, the core is filesystem
free, live mode cannot fall back to examples, root compatibility remains, the
authored selector excludes the surface from live state, and stale runtime
copies remain managed cleanup targets.
