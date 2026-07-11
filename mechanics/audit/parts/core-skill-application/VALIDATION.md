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
`surface-strength-detection`, finish-stage filtering, deterministic grouping,
the root compatibility aliases, schema validity, and committed-output parity.
The root tests retain repo-wide orchestration and public-route coverage.
