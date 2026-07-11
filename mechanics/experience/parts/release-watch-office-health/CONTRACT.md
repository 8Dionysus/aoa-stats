# Contract

## Input

Owner-local release, certification, watch, incident, installation, handoff,
and office-health observations.

## Output

Schema-backed candidate dashboards and summaries for derived observability.

## Boundary

No release approval, installation execution, rollback execution, service
authority, runtime write, assistant self-authority, or Tree of Sophia write is
granted by these contracts.

`schemas/release_health_summary_v1.json` has one owner in this part and
validates both paired release-health examples.

## Crosswalk

This non-catalog observation contract cross-routes to
`stats/operation-contracts/active/experience.release-watch-office-health.operation.json`;
the reciprocal route is enforced by
`mechanics/topology.json`.
