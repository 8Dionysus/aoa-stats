# Codex Plane Deployment Summaries

`aoa-stats` owns the derived view over Codex-plane deployment continuity.

This summary is derived from rollout receipts and typed deploy-status
snapshots. It does not authorize rollout, trust, or rollback.

## Minimum fields

- latest rollout state
- trust posture counts
- drift count
- rollback recommendation count
- stable MCP name set
- latest receipt reference

## Source precedence

Prefer:

1. live trust-state and rollout receipt contracts in `8Dionysus`
2. typed deploy-status snapshots in `aoa-sdk`
3. other derived counters only as secondary shaping signals

`aoa-stats` may summarize this family, but it does not overrule live trust
evidence.
