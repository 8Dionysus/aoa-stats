# Validation

Run the part-owned contract proof first:

```bash
python -m pytest -q mechanics/antifragility/parts/antifragility-vector/tests
```

Then run the cross-routed source, catalog, and placement checks:

```bash
python -m pytest -q tests/test_stats_source_home.py tests/test_summary_surface_catalog.py tests/test_mechanics_topology.py
```

See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

The checks must prove both sides of the boundary: the deferred entry exposes
its grounding and gaps, while no active vector surface or output exists.
