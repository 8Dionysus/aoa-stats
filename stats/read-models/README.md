# Stats read models

This branch is the authored source body behind the public summary-surface
catalog. Each active derived surface has one profile at
`active/<surface_name>.profile.json`; contract-only candidates live under
`deferred/`.

Profiles carry the stable question, derivation posture, stronger-owner inputs,
authority ceiling, public schema/output routes, consumer risk, live-state
posture, deterministic catalog order, and mechanics handoffs. The generated
catalog projects the public fields from these records. It is not an editable
copy of them.

`live_state_capable` is an executable selector, not a statement that every
committed surface is current. A `true` profile may be materialized and listed
by the local live refresh loop when its inputs resolve. A `false` profile stays
on its committed/reference route and is omitted from live output and the live
catalog, although refresh cleanup still removes any stale runtime copy.

The current managed inventory contains 25 active profiles; 16 are admitted to
live materialization. The nine reference-only profiles are Component Refresh,
Continuity Window, Codex Plane Deployment, Codex Rollout Operations, Codex
Rollout Drift, Rollout Campaign, Drift Review, Titan Incarnation, and Titan
Summon.
Continuity Window describes the posture represented by its committed
cross-owner example/catalog chain. Codex Plane Deployment describes the posture
represented by the committed 8Dionysus trust-state, regeneration-report, and
rollout-receipt examples. Neither example chain constitutes owner-runtime or
deploy-local state.

Codex Rollout Operations and Codex Rollout Drift describe the exact checked-in
trusted-history bundle; “latest” is bounded to that history. Rollout Campaign
and Drift Review describe a separate three-example cadence chain. Checked-in
history is not runtime state, and examples are not active cadence.

Use `committed_owner_example_chain` only when one owner repository publishes a
coherent set of checked-in examples that can drive a deterministic committed
reference snapshot. The token does not admit the surface to live
materialization and must never authorize an example fallback when deploy-local
inputs are missing.

`surface-profile.schema.json` constrains both active and deferred source
records. Importable implementation stays under `src/aoa_stats_builder/`,
public schemas stay under `schemas/`, and public derived outputs stay under
`generated/`.

## Lifecycle

- `active/`: exactly the profiles emitted in
  `generated/summary_surface_catalog.min.json`.
- `deferred/`: bounded contract candidates that are not emitted as active
  surfaces.

Do not activate a deferred profile by moving the file alone. Its producer,
input chain, public schema/output, mechanic route, and validation must become
real in the same bounded change.
