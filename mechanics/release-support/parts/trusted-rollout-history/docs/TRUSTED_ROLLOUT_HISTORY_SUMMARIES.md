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

## Compatibility seam

The filesystem-free core treats a missing or unresolved latest pointer as
invalid owner-history input. The root `scripts/build_views.py` helper retains
one older caller contract: when the latest pointer is absent, it returns a
detached copy of the final history row.

That fallback is compatibility behavior, not owner-history meaning. Its proof
lives with this mechanic beside the strict core; the root suite retains only
repo-wide build and fan-out assertions.

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
