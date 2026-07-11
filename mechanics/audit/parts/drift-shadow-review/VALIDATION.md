# Drift Shadow Review validation

Run the cross-routed source and placement checks from the repository root:

```bash
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q mechanics/audit/parts/drift-shadow-review/tests
python -m pytest -q mechanics/release-support/parts/rollout-campaign/tests
python -m pytest -q mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py
python -m pytest -q tests/test_build_views.py tests/test_stats_source_home.py tests/test_mechanics_topology.py
```

These checks prove strict shared cadence validation, explicit Audit ownership,
stable output, and reference-only live posture.
