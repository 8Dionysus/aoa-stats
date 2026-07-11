# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q tests/test_build_views.py tests/test_stats_source_home.py tests/test_mechanics_topology.py
```

When this part has a local `tests/` district, include that directory in the
focused pytest command.
