# Schools, lineages, and campaigns observability validation

Run from the repository root:

```bash
python mechanics/agon/parts/schools-lineages-campaigns-observability/scripts/build_agon_slc_stats_observability_registry.py --check
python mechanics/agon/parts/schools-lineages-campaigns-observability/scripts/validate_agon_slc_stats_observability_registry.py
python -m pytest -q mechanics/agon/parts/schools-lineages-campaigns-observability/tests/test_agon_slc_stats_observability_registry.py
```

The checks validate all eight entries, both schemas, uniqueness, and public
output freshness.
