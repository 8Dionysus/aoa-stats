# KAG observability validation

Run from the repository root:

```bash
python mechanics/agon/parts/kag-observability/scripts/build_agon_kag_stats_observability_registry.py --check
python mechanics/agon/parts/kag-observability/scripts/validate_agon_kag_stats_observability_registry.py
python -m pytest -q mechanics/agon/parts/kag-observability/tests/test_agon_kag_stats_observability_registry.py
```

The checks validate seven entries, both schemas, candidate posture, complete
stop lines, and generated drift.
