# Retention and rank observability contract

## Input

The part-local Wave XIV entries and explicit stop lines.

## Output

A schema-constrained registry published at
`generated/agon_retention_rank_stats_observability_registry.min.json`.

## Invariants

- entries are candidate-only and derived-summary-only
- no entry mutates rank, trust, jurisdiction, memory, or scheduling
- retention execution requires its stronger owner and review
- the generated registry carries the current part-local source route

## Crosswalk

This non-catalog observation contract cross-routes to
`stats/operation-contracts/active/agon.retention-rank-observability.operation.json`;
the reciprocal route is enforced by
`mechanics/topology.json`.
