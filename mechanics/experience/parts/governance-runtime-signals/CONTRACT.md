# Contract

## Input

Explicit owner-local governance events and queue observations.

## Output

Schema-backed derived summaries with bounded statuses, counts, and evidence
references.

## Boundary

Stats cannot decide an appeal, seal a vote, execute a veto, write policy, or
mutate runtime state.

## Crosswalk

This non-catalog observation contract cross-routes to
`stats/operation-contracts/active/experience.governance-runtime-signals.operation.json`;
the reciprocal route is enforced by
`mechanics/topology.json`.
