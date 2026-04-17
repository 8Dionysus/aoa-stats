# 2026-04-16: Stats Strength And Intake Governance

## Status

Accepted

## Context

`aoa-stats` had enough summary families to matter, but two weaknesses were
still visible:

1. the shared receipt ABI had no explicit admission table beyond the schema
   enum
2. the summary catalog could list surfaces, but it could not explain how
   strong each one was or where its authority ceiling lived

That made growth possible, but it also made overreading easier.

## Decision

`aoa-stats` now hardens growth through four linked moves:

1. keep the canonical receipt envelope plus an explicit event-kind registry
2. validate the `aoa-evals` mirror against the canonical envelope
3. publish surface-strength metadata inside the catalog itself
4. add `source_coverage_summary` so the stats layer can report where its own
   intake is thin

`antifragility_vector` remains contract-only until a real owner-linked repeated
stress family exists.

## Consequences

- `aoa-stats` becomes a more active participant in cross-repo work without
  pretending to be the owner of that work
- consumers can inspect the authority ceiling of each surface instead of
  inferring it from prose alone
- new event families now need an explicit registry entry, not just a schema
  edit
- downstream repos keep visible canaries that remind them `aoa-stats` is
  descriptive, not sovereign

## Verification

- `python scripts/validate_receipt_abi.py`
- `python scripts/validate_downstream_canaries.py`
- `python scripts/validate_repo.py`
- `python -m pytest -q tests`
