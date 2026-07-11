# Validation

Run from the repository root:

```bash
python -m pytest -q mechanics/audit/parts/object-observation/tests/test_object_observation.py
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q tests/test_build_views.py tests/test_stats_source_home.py tests/test_mechanics_topology.py
```

The focused part-local test covers input-first observation, temporal-latest
receipt selection, supplied-order last evaluation/progression verdicts,
non-mutating projection, root compatibility aliases, schema validity, and
committed-output parity. It records ordered-input compatibility and does not
claim permutation invariance or canonical owner chronology. The root tests
retain repo-wide orchestration and public-route coverage.
