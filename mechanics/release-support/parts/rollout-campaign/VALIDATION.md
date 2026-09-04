# Rollout Campaign validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/release-support/parts/rollout-campaign/tests
```

See the nearest owner validation route (../../../audit/parts/drift-shadow-review/VALIDATION.md) for this procedure. See the nearest owner validation route (../../../recurrence/parts/live-receipt-refresh/VALIDATION.md) for this procedure. See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

These checks prove strict internal example coherence, filesystem-free shared
projection, campaign/review ownership separation, stable public output, and
reference-only live posture.
