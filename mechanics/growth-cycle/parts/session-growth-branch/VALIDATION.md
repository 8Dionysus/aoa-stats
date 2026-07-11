# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/growth-cycle/tests/test_growth_cycle_projections.py
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
```

The package-level test is intentional: it constrains the shared deterministic
core and the root compatibility facade across all four Growth Cycle read
models.
