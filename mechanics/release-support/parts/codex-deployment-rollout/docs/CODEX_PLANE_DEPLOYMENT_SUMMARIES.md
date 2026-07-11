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

When `8Dionysus` also publishes source-owned cadence windows under
`examples/rollout_campaign_window.example.json`,
`examples/drift_review_window.example.json`, and
`examples/rollback_followthrough_window.example.json`, `aoa-stats` may derive:

- `generated/rollout_campaign_summary.min.json`
- `generated/drift_review_summary.min.json`

These cadence companions may expose:

- one current campaign ref and campaign state
- whether one bounded review is still pending
- whether one rollback-followthrough window is ready
- simple lineage-ref counts when stronger upstream refs already exist
- named drift-signal counts and decision counts

They remain descriptive only.
They do not authorize campaign decisions, cadence closure, or rollback posture.

## Source precedence

Prefer:

1. live trust-state and rollout receipt contracts in `8Dionysus`
2. checked-in trusted rollout history in `8Dionysus/generated/codex/rollout/`
3. source-owned cadence windows in `8Dionysus/examples/*.example.json`
4. typed deploy-status snapshots in `aoa-sdk`
5. other derived counters only as secondary shaping signals

`aoa-stats` may summarize this family, but it does not overrule live trust
evidence.
