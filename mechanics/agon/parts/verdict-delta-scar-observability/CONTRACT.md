# Verdict, delta, and scar observability contract

## Input

Part-local candidate summary declarations for verdict, delta, scar, and their
review boundaries.

## Output

A deterministic derived registry published at
`generated/agon_vds_stats_observability_registry.min.json`.

## Invariants

- the registry remains Wave XI, non-live, and runtime-effect free
- every summary states what it may and must not emit
- stats does not become verdict authority, a value system, or a durable scar
  writer
- the boundary documentation remains part of this operation package

## Crosswalk

This non-catalog observation contract cross-routes to
`stats/operation-contracts/`; the reciprocal route is enforced by
`mechanics/topology.json`.
