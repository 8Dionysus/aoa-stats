# Stats prebinding contract

## Input

The part-local Wave VII seed, bounded Agon observation names, and explicit
candidate outputs.

## Output

A deterministic prebinding registry published at
`generated/agon_stats_prebinding_registry.min.json`.

## Invariants

- every record is pre-protocol and has no runtime effect
- no prebinding opens an arena, writes durable state, mutates rank, promotes to
  Tree of Sophia, or runs hidden scheduling
- stats may name derived summaries but may not judge an agent or grant action
  authority
- the public registry identifies the part-local seed as its source

## Crosswalk

This non-catalog observation contract cross-routes to
`stats/operation-contracts/`; the reciprocal route is enforced by
`mechanics/topology.json`.
