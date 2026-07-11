# Validation

Run the focused core/adapter contract first from the repository root:

```bash
python -m pytest -q mechanics/antifragility/parts/stress-recovery-windows/tests/test_stress_recovery_projection.py
```

That test proves committed-output parity, schema validity, input non-mutation,
filesystem-free core placement, exact `aoa-evals` ref resolution, explicit-only
legacy aliasing, and suppression for missing or malformed reports.

Then run the complete part and cross-routed placement checks:

```bash
python -m pytest -q mechanics/antifragility/parts/stress-recovery-windows/tests
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q tests/test_build_views.py tests/test_stats_source_home.py tests/test_mechanics_topology.py
```

For live-admission changes, also run the refresh-focused suite because a green
manual build does not prove that the owner source is observed:

```bash
python -m pytest -q mechanics/recurrence/parts/live-receipt-refresh/tests
```

Do not replace the exact live adapter with the committed-reference loader to
make a live test pass. Activation must satisfy the owner-source and observation
conditions in AOST-D-0004.
