# Trusted Rollout History Summaries

`aoa-stats` derives two bounded companions from the checked-in trusted rollout
history published by `8Dionysus`:

- `generated/codex_rollout_operations_summary.min.json`
- `generated/codex_rollout_drift_summary.min.json`

The source bundle contains deploy history, regeneration campaigns, rollback
windows, and the compact latest pointer under
`8Dionysus/generated/codex/rollout/`. The source adapter loads exactly those
four files. A filesystem-free core validates lifecycle and cross-reference
coherence before producing either summary.

## Operations summary

The operations projection exposes bounded historical counts, the source-owned
latest history pointer, the latest stable campaign reference, active drift and
rollback references, and the upstream source refs.

## Drift summary

The drift projection resolves the history entry named by the latest pointer and
exposes its drift state, explicit repair-attempt flag, first drift reference,
and descriptive rollback requirement.

## Source and freshness boundary

“Latest” means latest inside the checked-in owner-history bundle. It does not
mean current deploy-local workspace state. The four source files are distinct
from:

- the deploy-local trust/regeneration/receipt trio owned by the Codex Plane
  deployment route
- the campaign, drift-review, and rollback-followthrough cadence examples

Neither profile is admitted to local live materialization. A stale runtime copy
must be cleaned rather than refreshed from committed history.

These summaries may shape review attention. They do not authorize rollout,
stabilization, repair, or rollback and never outrank the owner history.
