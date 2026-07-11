# Drift Review Summary

`aoa-stats` may derive one bounded drift-review summary from the source-owned
`8Dionysus` cadence windows.

This summary counts the named drift signals and explicit review decision
represented by the committed example chain without turning `aoa-stats` into
campaign truth or claiming a current review.

## Minimum fields

- represented `campaign_ref`
- represented `review_ref`
- one bounded review-window count
- named drift-signal counts
- explicit decision counts
- whether a rollback-followthrough window is ready

## Boundary

The shared cadence core rejects missing decisions, cross-campaign refs,
invalid booleans, incoherent rollback anchors, and unsupported status/decision
combinations. It validates only the internal three-example chain and does not
claim freshness against checked-in trusted rollout history.

The profile is not live-capable. Live refresh removes stale runtime copies
instead of replaying the examples.

This summary may highlight where review pressure remains.
It does not:

- narrate drift without evidence
- authorize rollback
- overrule source-owned cadence windows
- replace checked-in rollout history
