# Audit validation

Run from the repository root when the shared core-skill observation core or
either of its two projections changes:

```bash
python -m pytest -q mechanics/audit/tests/test_core_skill_observation.py
```

This package-level route is the single human-authored owner of the cross-part
suite shared by `core-skill-application` and `surface-strength-detection`.
Their part routes may add a genuinely local check, but must link here rather
than copy this invocation. Use
[shared repository checks](../../VALIDATION.md#shared-repository-checks) only
when cross-mechanic or generated-parity coverage is required.
