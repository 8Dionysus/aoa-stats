# Mechanical-trial observability contract

## Input

The part-local mechanical-trial seed and its declared source surfaces.

## Output

A deterministic candidate-only registry published at
`generated/agon_mechanical_trial_stats_observability_registry.min.json`.

## Invariants

- summaries remain candidate-only and do not become a live trial protocol
- owner source surfaces are observed, not rewritten
- digest and count are derived from the complete local seed
- stale generated output is rejected

## Crosswalk

This non-catalog observation contract cross-routes to
`stats/operation-contracts/`; the reciprocal route is enforced by
`mechanics/topology.json`.
