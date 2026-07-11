# Stats read models

This branch is the authored source body behind the public summary-surface
catalog. Each active derived surface has one profile at
`active/<surface_name>.profile.json`; contract-only candidates live under
`deferred/`; removed outputs with an outstanding cleanup obligation leave a
minimal tombstone under `retired/`.

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

The current inventory contains 24 active profiles and one retired-output
tombstone. Of the active profiles, 11 are admitted to live materialization and
13 are reference-only: Owner Landing,
Codex Plane Deployment, Codex Rollout Operations, Codex Rollout Drift, Rollout
Campaign, Drift Review, Continuity Window, Component Refresh, Memory Movement,
Route Progression, Runtime Closeout, Titan Incarnation, and Stress Recovery
Window.
Continuity Window describes the posture represented by its committed
cross-owner example/catalog chain. Codex Plane Deployment describes the posture
represented by the committed 8Dionysus trust-state, regeneration-report, and
rollout-receipt examples. Neither example chain constitutes owner-runtime or
deploy-local state.

Codex Rollout Operations and Codex Rollout Drift describe the exact checked-in
trusted-history bundle; “latest” is bounded to that history. Rollout Campaign
and Drift Review describe a separate three-example cadence chain. Checked-in
history is not runtime state, and examples are not active cadence.

Owner Landing and Stress Recovery Window currently describe only committed
receipt/report examples: neither has a real active owner publisher. Memory
Movement reads a real reviewed `aoa-memo` corpus, but the automatic refresh
mechanic does not observe changes to its four source roots. A current source is
necessary but not sufficient for continuously advertised live state; all three
profiles stay false until their missing producer or refresh observation route
exists and is tested.

The receipt-backed Audit profiles retain their existing live posture but have
two explicit implementation boundaries. Core Skill Application and Surface
Detection share one finish-stage receipt selector; Object Observation reads
the full active receipt feed through a separate core. Sharing implementation
does not merge their authored questions, source ceilings, mechanic routes, or
catalog identities.

Route Progression retains a committed legacy numeric snapshot, but not live
admission. The RPG center owns progression-reading vocabulary and stop-lines;
`aoa-skills` owns the current semantic progression receipt, `aoa-agents` owns
the agent-layer overlay, and `aoa-sdk` owns typed transport. Because the owner
contract intentionally uses descriptive `axis_delta_summary` values rather
than a numeric score, aoa-stats rejects that shape instead of assigning
numbers. Future live activation needs an explicit cross-owner semantic
projection contract.

Runtime Closeout retains the committed historical `runtime_wave_closeout_receipt`
snapshot, but not live admission. The current `abyss-stack` producer emits
`runtime_trial_closeout_receipt` to a different owner-local log, while
`aoa-sdk` exposes a separate `runtime_return_closeout_receipt` contract. None
is an implicit alias. Future live activation needs one owner-approved receipt
ABI, an observed source, registry and watcher parity, and end-to-end proof.

Repeated Window remains receipt-backed and live-capable, but its claim is
deliberately narrower than its historical name. It groups admitted receipts by
the calendar-date prefix already present in `observed_at` and reports conserved
counts. It does not compare states or infer that change, recurrence, cadence, or
causality occurred.

Titan Incarnation validates one exact committed cross-owner example chain: the
`aoa-agents` operator and runtime rosters plus the `aoa-sdk` v2 session receipt.
The shared 5/3/2 partition is a reference projection, not current incarnation
state. Titan Summon had no committed owner ledger input, so its no-ledger zero
baseline carried no active fact and is no longer built or cataloged. Its v1
schema remains as contract history and its retired profile keeps stale-output
and consumer cleanup deterministic. AOST-D-0007 records the evidence boundary;
AOST-D-0008 records the retirement lifecycle. A future observed Summon surface
needs a new active profile, real owner ledger, producer, and refresh proof.

Use `committed_owner_example_chain` only when one owner repository publishes a
coherent set of checked-in examples that can drive a deterministic committed
reference snapshot. The token does not admit the surface to live
materialization and must never authorize an example fallback when deploy-local
inputs are missing.

`surface-profile.schema.json` constrains active, deferred, and retired source
records. Importable implementation stays under `src/aoa_stats_builder/`,
public schemas stay under `schemas/`, and public derived outputs stay under
`generated/`.

## Lifecycle

- `active/`: exactly the profiles emitted in
  `generated/summary_surface_catalog.min.json`.
- `deferred/`: bounded contract candidates that are not emitted as active
  surfaces.
- `retired/`: cleanup/provenance tombstones for removed outputs; they carry no
  builder, generated payload, catalog entry, or active mechanic handoff.

Do not activate a deferred profile by moving the file alone. Its producer,
input chain, public schema/output, mechanic route, and validation must become
real in the same bounded change.

Do not reactivate a retired tombstone. Reintroduction is a new active-surface
decision with current evidence and consumer review.
