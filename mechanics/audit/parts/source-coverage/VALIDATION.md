# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/audit/parts/source-coverage/tests/test_source_coverage.py tests/test_stats_source_home.py tests/test_mechanics_topology.py
```

See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

The part-local suite proves exact committed parity, registry and receipt order
invariance, count conservation, non-mutation, explicit missing-registry
posture, dominance thresholds, and the absence of verdict or route authority.
