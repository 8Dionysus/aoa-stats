# Epistemic observability contract

## Input

Part-local epistemic candidate summaries with owner, review, runtime, and
forbidden-effect declarations.

## Output

A deterministic registry published at
`generated/agon_epistemic_stats_observability_registry.min.json`.

## Invariants

- all eight summaries remain non-live and candidate-only
- owner truth is observed, not replaced
- stats cannot rewrite doctrine, decide truth, promote to KAG or Tree of
  Sophia, or take verdict and retention authority
- each summary carries the complete forbidden-effect boundary

## Crosswalk

This non-catalog observation contract cross-routes to
`stats/operation-contracts/active/agon.epistemic-observability.operation.json`;
the reciprocal route is enforced by
`mechanics/topology.json`.
