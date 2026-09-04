# Growth Cycle validation

Run from the repository root when the shared Growth Cycle projection core, any
of its four read models, or the compatibility facade changes:

```bash
python -m pytest -q mechanics/growth-cycle/tests/test_growth_cycle_projections.py
```

This mechanic-level route is the single human-authored owner of the cross-part
suite. Part routes may add a genuinely local check, but must link here rather
than copy this invocation. Use [shared repository checks](../../VALIDATION.md#shared-repository-checks)
only when cross-mechanic or generated-parity coverage is required.
