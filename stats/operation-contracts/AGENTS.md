# AGENTS.md

Route card for `stats/operation-contracts/`.

## Role

This branch owns one schema-backed source record for each of the active
part-local stats operations that do not publish a public catalog read model.
Each record owns the bounded stats question, input maturity, authority ceiling,
consumer risk, forbidden inference boundary, and return to stronger owners. The
payload, scripts, examples, tests, and operation lifecycle remain with the
named mechanic part.

## Read before editing

1. `../AGENTS.md`
2. `README.md`
3. `operation-contract.schema.json`
4. the selected record under `active/`
5. the exact mechanic contract, validation card, and topology part named by
   that record

## Law

- Every routed mechanic part has exactly one record under `active/`. The
  record's `mechanic_route` and the topology part's
  `stats_operation_contract_ref` must point to one another.
- Derive active inventory from authored records and reciprocal manifest and
  topology links. Require a non-empty family, but do not freeze the current
  operation count in validation or tests.
- Keep `payload_class`, `mechanic_contract_ref`, and `validation_ref` identical
  to the named topology part.
- Give every `owner_truth_inputs.owner_repo` an exact `owner_return_routes`
  entry, including a bounded return beneath the canonical mechanic owner.
- State whether stronger-owner inputs are actually bound, merely declared by
  reference, or still symbolic. Do not turn a planned input into current
  evidence. A bound input requires a mechanic-local proof ref and explicit
  registration in the source-home validator.
- Do not add a public surface profile merely to make a part visible here.
- Do not copy mechanic schemas, examples, scripts, tests, metric lists, or
  generated output under `stats/`.
- Part-local registries, metrics, examples, and prose remain weaker than their
  stronger-owner evidence.

## Verify

```bash
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q tests/test_stats_source_home.py tests/test_mechanics_topology.py
```
