# Mechanical-trial observability validation

Run from the repository root:

```bash
python mechanics/agon/parts/mechanical-trial-observability/scripts/build_agon_mechanical_trial_stats_observability.py --check
python mechanics/agon/parts/mechanical-trial-observability/scripts/validate_agon_mechanical_trial_stats_observability.py
python -m pytest -q mechanics/agon/parts/mechanical-trial-observability/tests/test_agon_mechanical_trial_stats_observability.py
```

The focused test also proves that a deliberately stale digest is rejected.
