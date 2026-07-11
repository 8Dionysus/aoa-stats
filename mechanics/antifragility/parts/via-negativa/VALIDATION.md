# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q tests/test_stats_source_home.py tests/test_mechanics_topology.py
```

These checks prove the authored question and reciprocal route. The checklist
is human review guidance; no automated remove, suppress, or quarantine action
is claimed.
