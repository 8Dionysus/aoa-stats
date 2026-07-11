# AGENTS.md

Route card for `stats/operation-contracts/`.

## Role

This branch owns the source-family meaning and authority ceiling for active
part-local stats operations that do not publish a public catalog read model.
The payload, scripts, examples, tests, and operation lifecycle remain with the
named mechanic part.

## Law

- Every routed mechanic part must appear in `stats/source_home.manifest.json`,
  `mechanics/topology.json`, and the part's `stats_source_family_refs`.
- Do not add a public surface profile merely to make a part visible here.
- Do not duplicate part payload under `stats/`.
- Part-local registries, metrics, examples, and prose remain weaker than their
  stronger-owner evidence.

## Verify

```bash
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q tests/test_stats_source_home.py tests/test_mechanics_topology.py
```
