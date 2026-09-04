# Drift Shadow Review validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/audit/parts/drift-shadow-review/tests
python -m pytest -q mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py
```

See the nearest owner validation route (../../../release-support/parts/rollout-campaign/VALIDATION.md) for this procedure. See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

These checks prove strict shared cadence validation, explicit Audit ownership,
stable output, and reference-only live posture.
