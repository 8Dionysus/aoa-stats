# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/method-growth/parts/supersession-pruning/tests/test_supersession_pruning.py
```

See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

The part-local suite constrains Supersession Pruning and its root compatibility
alias. It proves that explicit turnover carried by the two retained landing
receipt kinds still reaches this output in any receipt order without restoring
the retired standalone Owner Landing builder. Candidate Lineage owns its
separate builder proof under its own part.
