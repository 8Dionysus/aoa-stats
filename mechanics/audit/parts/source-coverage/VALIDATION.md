# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q mechanics/audit/parts/source-coverage/tests/test_source_coverage.py tests/test_stats_source_home.py tests/test_mechanics_topology.py
```

The part-local suite proves exact committed parity, registry and receipt order
invariance, count conservation, non-mutation, explicit missing-registry
posture, dominance thresholds, and the absence of verdict or route authority.
