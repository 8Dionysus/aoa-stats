# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/method-growth/parts/candidate-lineage/tests/test_candidate_lineage.py
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
```

This part-local suite constrains Candidate Lineage behavior and its root
compatibility alias. Supersession Pruning owns separate proof even though both
builders reuse the same filesystem-free lifecycle core.
