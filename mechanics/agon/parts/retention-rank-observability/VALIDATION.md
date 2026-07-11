# Retention and rank observability validation

Run from the repository root:

```bash
python mechanics/agon/parts/retention-rank-observability/scripts/build_agon_retention_rank_stats_observability_registry.py --check
python mechanics/agon/parts/retention-rank-observability/scripts/validate_agon_retention_rank_stats_observability.py
python -m pytest -q mechanics/agon/parts/retention-rank-observability/tests/test_agon_retention_rank_stats_observability.py
```

The checks validate both entry and registry schemas and compare the public
output with a fresh part-local build.
