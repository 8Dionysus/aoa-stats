# Validation

Run from the repository root:

```bash
python -m pytest -q mechanics/audit/tests/test_core_skill_observation.py
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q tests/test_build_views.py tests/test_stats_source_home.py tests/test_mechanics_topology.py
```

The package-level test is intentional: it covers the core shared with
`core-skill-application`, finish-stage selection, the legacy missing-context
`activated` bucket, supplied-order date-window bounds, advisory counters,
non-mutating projection, root compatibility aliases, schema validity, and
committed-output parity. It preserves extraction compatibility; it does not
prove owner activation or strict candidate-count payload validation.
