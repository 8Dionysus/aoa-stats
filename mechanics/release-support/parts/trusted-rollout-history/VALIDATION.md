# Trusted Rollout History validation

Run from the repository root:

```bash
python -m pytest -q mechanics/release-support/parts/trusted-rollout-history/tests
```

See the nearest owner validation route (../../../recurrence/parts/live-receipt-refresh/VALIDATION.md) for this procedure. See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

These checks prove the four-file owner-history chain, filesystem-free core,
the strict-core versus legacy-facade lookup seam, stable public outputs,
false-live selectors, and managed stale cleanup.
