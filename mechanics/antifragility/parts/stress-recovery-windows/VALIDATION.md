# Validation

Run the focused core/adapter contract first from the repository root:

```bash
python -m pytest -q mechanics/antifragility/parts/stress-recovery-windows/tests/test_stress_recovery_projection.py
```

That test proves committed-output parity, schema validity, input non-mutation,
filesystem-free core placement, canonical `aoa-evals` ref resolution, absence
of retired bundle-path translation, and suppression for missing or malformed
reports.

Then run the complete part and cross-routed placement checks:

```bash
python -m pytest -q mechanics/antifragility/parts/stress-recovery-windows/tests
```

See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

For live-admission changes, also run the refresh-focused suite because a green
manual build does not prove that the owner source is observed:

```bash
python -m pytest -q mechanics/recurrence/parts/live-receipt-refresh/tests
```

Do not add a committed-example fallback to make a live test pass. Activation
must satisfy the owner-source and observation conditions in AOST-D-0004.
