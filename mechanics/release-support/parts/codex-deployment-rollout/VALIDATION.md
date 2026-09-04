# Codex Plane Deployment validation

Run from the repository root:

```bash
python -m pytest -q mechanics/release-support/parts/codex-deployment-rollout/tests
```

See the nearest owner validation route (../../../recurrence/parts/live-receipt-refresh/VALIDATION.md) for this procedure. See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

These checks prove the reference chain is coherent, the core is filesystem
free, live mode cannot fall back to examples, root compatibility remains, the
authored selector excludes the surface from live state, and stale runtime
copies remain managed cleanup targets.
