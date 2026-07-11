# Rollout Campaign Summary

`aoa-stats` may derive one bounded campaign-cadence summary from the
source-owned `8Dionysus` campaign window examples.

This summary exposes the posture represented by that committed example chain
without moving campaign authority out of `8Dionysus` or claiming current
cadence state.

## Minimum fields

- represented `campaign_ref`
- represented campaign state
- whether one bounded review is still pending
- whether one rollback-followthrough window is ready
- simple lineage-ref counts when stronger upstream refs are present

## Boundary

The adapter reads only the campaign, drift-review, and rollback-followthrough
examples. The core requires their internal refs, status/decision combinations,
booleans, and timestamps to be coherent. It deliberately does not load
`rollout_latest.min.json`, so this projection cannot certify that the example
still matches the latest checked-in rollout history; use the owner validator
for that wider assertion.

The profile is not live-capable. Live refresh removes stale runtime copies
instead of replaying this example chain.

This summary may shape attention.
It does not:

- authorize campaign closure
- decide reanchor or rollback
- replace checked-in rollout history
- replace source-owned cadence windows
