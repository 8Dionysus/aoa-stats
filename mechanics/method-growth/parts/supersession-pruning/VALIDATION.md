# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/method-growth/parts/supersession-pruning/tests/test_supersession_pruning.py
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
```

The part-local suite constrains Supersession Pruning and its root compatibility
alias. It proves that explicit turnover carried by the two retained landing
receipt kinds still reaches this output in any receipt order without restoring
the retired standalone Owner Landing builder. Candidate Lineage owns its
separate builder proof under its own part.
