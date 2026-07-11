# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/method-growth/tests/test_candidate_lifecycle.py
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
```

The package-level test is intentional: it constrains the shared lifecycle core
and the root compatibility facade across both active Method Growth parts.
