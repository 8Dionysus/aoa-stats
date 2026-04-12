# Codex Plane Deployment Summaries

`aoa-stats` owns the derived view over Codex-plane deployment continuity and the
checked-in trusted rollout operations companions.

This summary is derived from rollout receipts and typed deploy-status
snapshots. It does not authorize rollout, trust, or rollback.

## Minimum fields

- latest rollout state
- trust posture counts
- drift count
- rollback recommendation count
- stable MCP name set
- latest receipt reference

## Trusted rollout operations companions

When `8Dionysus` publishes checked-in shared-root rollout campaign history under
`generated/codex/rollout/`, `aoa-stats` may derive two bounded companions:

- `generated/codex_rollout_operations_summary.min.json`
- `generated/codex_rollout_drift_summary.min.json`

These summaries may expose:

- latest rollout campaign ref
- latest rollout state
- latest stable rollout campaign ref
- counts by rollout state
- latest drift window ref
- latest drift state
- whether bounded repair was attempted
- whether rollback remained required

They remain descriptive only.
They do not authorize rollout, stabilization, or rollback.

## Source precedence

Prefer:

1. live trust-state and rollout receipt contracts in `8Dionysus`
2. checked-in trusted rollout history in `8Dionysus/generated/codex/rollout/`
3. typed deploy-status snapshots in `aoa-sdk`
4. other derived counters only as secondary shaping signals

`aoa-stats` may summarize this family, but it does not overrule live trust
evidence.
