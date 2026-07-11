# Sophian observability contract

## Input

Part-local Sophian candidate summaries and their explicit review and authority
boundaries.

## Output

A deterministic candidate registry published at
`generated/agon_sophian_stats_observability_registry.min.json`.

## Invariants

- all six summaries remain non-live and candidate-only
- stats does not become philosophical source truth, doctrine, canon, or Tree of
  Sophia promotion authority
- owner review remains required
- generated count, digest, and summaries are derived from the part-local seed

## Crosswalk

This non-catalog observation contract cross-routes to
`stats/operation-contracts/active/agon.sophian-observability.operation.json`;
the reciprocal route is enforced by
`mechanics/topology.json`.
