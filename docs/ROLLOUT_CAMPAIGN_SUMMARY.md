# Rollout Campaign Summary

`aoa-stats` may derive one bounded campaign-cadence summary from the
source-owned `8Dionysus` campaign window examples.

This summary exists to expose the current cadence posture without moving
campaign authority out of `8Dionysus`.

## Minimum fields

- current `campaign_ref`
- current campaign state
- whether one bounded review is still pending
- whether one rollback-followthrough window is ready
- simple lineage-ref counts when stronger upstream refs are present

## Boundary

This summary may shape attention.
It does not:

- authorize campaign closure
- decide reanchor or rollback
- replace checked-in rollout history
- replace source-owned cadence windows
