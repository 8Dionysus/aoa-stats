# Verdict, delta, and scar observability validation

Run from the repository root:

```bash
python mechanics/agon/parts/verdict-delta-scar-observability/scripts/build_agon_vds_stats_observability_registry.py --check
python mechanics/agon/parts/verdict-delta-scar-observability/scripts/validate_agon_vds_stats_observability.py
python -m pytest -q mechanics/agon/parts/verdict-delta-scar-observability/tests/test_agon_vds_stats_observability.py
```

The checks prove deterministic publication and the non-authority stop lines.
