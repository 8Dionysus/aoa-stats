# Sophian observability validation

Run from the repository root:

```bash
python mechanics/agon/parts/sophian-observability/scripts/build_agon_sophian_stats_observability_registry.py --check
python mechanics/agon/parts/sophian-observability/scripts/validate_agon_sophian_stats_observability_registry.py
python -m pytest -q mechanics/agon/parts/sophian-observability/tests/test_agon_sophian_stats_observability_registry.py
```

The checks validate the six part-local summaries and public output freshness.
