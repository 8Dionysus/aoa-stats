# Codex Plane Deployment Summaries

`aoa-stats` owns a derived view over Codex Plane deployment continuity and
separate checked-in rollout-operation companions.

## Current deployment source posture

The v1 deployment summary is a committed reference snapshot, not current live
workspace state. It reads the coherent trust-state, regeneration-report, and
rollout-receipt examples published by `8Dionysus`.

An explicit reference adapter loads those examples and hands an immutable
bundle to a filesystem-free validation/projection core. The core checks schema
versions, selected workspace-root and id coherence, that both precursor
timestamps do not postdate the receipt, verified/doctor agreement, and
required stable-name evidence before projection. Additional project-local MCP
names are not drift. Stable MCP names come from the stronger
trust/regeneration chain rather than the narrower `aoa-sdk` example, and
non-doctor pre-apply drift does not manufacture a rollback recommendation.

The authored profile is therefore not live-capable. Local live refresh omits
the surface and removes stale copies instead of replaying the examples under
`state/generated/`.

This summary does not authorize rollout, trust, doctor success, or rollback.

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

1. the deploy-local trust-state artifact at the explicit workspace root
2. the deploy-local rollout receipt and doctor outcome
3. the deploy-local regeneration report
4. the `aoa-sdk` typed deploy-status readout of those same artifacts
5. this derived stats summary

The committed 8Dionysus example chain demonstrates the shape but never outranks
any of those live surfaces.

## Future live activation

Live mode has a separate no-fallback adapter for the three paths documented by
`8Dionysus` under `.codex/generated/rollout/`. Missing artifacts mean no live
deployment summary. Invalid or incoherent artifacts fail. Activation also
requires a real producer and a watcher or explicit refresh signal before the
profile may become live-capable.

The `aoa-sdk` deploy-status API remains useful as a parallel typed consistency
check. Stats does not add an SDK runtime dependency merely to reread the same
three files.

## Companion boundary

The rollout-history and cadence Campaign/Drift summaries below use different
checked-in source contexts. They are intentionally outside this deployment
source-mode refactor.

`aoa-stats` may summarize this family, but it does not overrule live trust
evidence.
