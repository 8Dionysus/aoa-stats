# KAG observability contract

## Input

Part-local candidate summaries for KAG promotion pressure, survival,
rejection, review latency, pattern-family health, and threshold pressure.

## Output

A deterministic candidate registry published at
`generated/agon_kag_stats_observability_registry.min.json`.

## Invariants

- KAG candidates are not canon or source truth
- promotion requires owner review and cannot follow from a single event
- stats and eval surfaces are not promotion authorities
- no direct KAG or Tree of Sophia promotion, verdict, scar, retention, rank,
  trust, or hidden scheduler effect is allowed

## Crosswalk

This non-catalog observation contract cross-routes to
`stats/operation-contracts/`; the reciprocal route is enforced by
`mechanics/topology.json`.
