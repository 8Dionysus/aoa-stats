# Schools, lineages, and campaigns observability contract

## Input

Part-local candidate summaries for school, lineage, and campaign observation.

## Output

A deterministic schema-backed registry published at
`generated/agon_slc_stats_observability_registry.min.json`.

## Invariants

- school is not authority, lineage is not canon, and campaign is not a live
  arena
- source owners retain truth and review authority
- every summary remains non-live, non-authoritative, and candidate-only
- all declared stop lines and forbidden effects remain present

## Crosswalk

This non-catalog observation contract cross-routes to
`stats/operation-contracts/`; the reciprocal route is enforced by
`mechanics/topology.json`.
