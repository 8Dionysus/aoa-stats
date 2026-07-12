# Validation

Run the part-owned contract proof first:

```bash
python -m pytest -q mechanics/antifragility/parts/antifragility-vector/tests
```

Then run the cross-routed source, catalog, and placement checks:

```bash
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q tests/test_stats_source_home.py tests/test_summary_surface_catalog.py tests/test_mechanics_topology.py
```

The checks must prove both sides of the boundary: the deferred entry exposes
its grounding and gaps, while no active vector surface or output exists.
