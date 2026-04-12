# Drift Review Summary

`aoa-stats` may derive one bounded drift-review summary from the source-owned
`8Dionysus` cadence windows.

This summary exists to count named drift signals and explicit review decisions
without turning `aoa-stats` into campaign truth.

## Minimum fields

- current `campaign_ref`
- current `review_ref`
- one bounded review-window count
- named drift-signal counts
- explicit decision counts
- whether a rollback-followthrough window is ready

## Boundary

This summary may highlight where review pressure remains.
It does not:

- narrate drift without evidence
- authorize rollback
- overrule source-owned cadence windows
- replace checked-in rollout history
