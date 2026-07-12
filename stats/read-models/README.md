# Stats read models

This branch is the authored source body behind the public summary-surface
catalog. Each active derived surface has one profile at
`active/<surface_name>.profile.json`; contract-only candidates live under
`deferred/`; removed outputs with an outstanding cleanup obligation leave a
minimal tombstone under `retired/`.

Profiles carry the stable question, derivation posture, stronger-owner inputs,
authority ceiling, public schema/output routes, consumer risk, live-state
posture, stable catalog slot, and mechanics handoffs. The generated
catalog projects the public fields from these records. It is not an editable
copy of them.

Deferred profiles carry the same grounding vocabulary where it is already
known, plus explicit `activation_gaps`. They do not carry an active catalog
slot, output route, or live-state selector.

`live_state_capable` is an executable selector, not a statement that every
committed surface is current. A `true` profile may be materialized and listed
by the local live refresh loop when its inputs resolve. A `false` profile stays
on its committed/reference route and is omitted from live output and the live
catalog, although refresh cleanup still removes any stale runtime copy.

The current inventory contains 22 active profiles and three retired-output
tombstones. Of the active profiles, 11 are admitted to live materialization and
11 are reference-only:
Codex Plane Deployment, Codex Rollout Operations, Codex Rollout Drift, Rollout
Campaign, Drift Review, Continuity Window, Component Refresh, Memory Movement,
Route Progression, Titan Incarnation, and Stress Recovery
Window.
Continuity Window describes the posture represented by its committed
cross-owner example/catalog chain. Codex Plane Deployment describes the posture
represented by the committed 8Dionysus trust-state, regeneration-report, and
rollout-receipt examples. Neither example chain constitutes owner-runtime or
deploy-local state.

The additional deferred profile is Antifragility Vector. ATM10-Agent emits a
real `stressor_receipt_v1` for the bounded retrieval-only fallback, but its
`adaptation_delta_v1` remains contract/example only. The linked
`aoa-antifragility-posture` eval is still draft/example only, neither chain
is registered as a stats live source, and no repeated same-family window
demonstrates movement. The deferred catalog publishes those stronger-owner
routes and gaps; it does not publish a vector surface.

Codex Rollout Operations and Codex Rollout Drift describe the exact checked-in
trusted-history bundle; “latest” is bounded to that history. Rollout Campaign
and Drift Review describe a separate three-example cadence chain. Checked-in
history is not runtime state, and examples are not active cadence.

Stress Recovery Window currently describes only committed report examples and
has no real active owner publisher. Memory Movement reads a real reviewed
`aoa-memo` corpus, but the automatic refresh
mechanic does not observe changes to its four source roots. A current source is
necessary but not sufficient for continuously advertised live state; both
active profiles stay false until their missing producer or refresh observation
route exists and is tested. Owner Landing is no longer an active reference
profile: its example-only aggregate is retired while its event kinds remain
inputs to Supersession Drop.

The receipt-backed Audit profiles retain their existing live posture but have
three explicit implementation boundaries. Core Skill Application and Surface
Detection share one finish-stage receipt selector; Object Observation reads
the full active receipt feed through a separate core; Source Coverage audits
that feed against the optional registry baseline through its own core and
part-local invariant suite. Sharing inputs does not merge their authored
questions, source ceilings, mechanic routes, catalog identities, or producer
and consumer proof homes.

Route Progression retains a committed legacy numeric snapshot, but not live
admission. The RPG center owns progression-reading vocabulary and stop-lines;
`aoa-skills` owns the current semantic progression receipt, `aoa-agents` owns
the agent-layer overlay, and `aoa-sdk` owns typed transport. Because the owner
contract intentionally uses descriptive `axis_delta_summary` values rather
than a numeric score, aoa-stats rejects that shape instead of assigning
numbers. Future live activation needs an explicit cross-owner semantic
projection contract.

Runtime Closeout is no longer an active reference profile. Its standalone
historical `runtime_wave_closeout_receipt` projection has no current publisher
or direct consumer, so the builder, payload, catalog entry, and repo-local
Checkpoint package are retired. The event kind remains generic evidence for
Object, Repeated Window, and Source Coverage; the schema remains contract
history. Current `abyss-stack` trial and `aoa-sdk` return contracts are not
implicit aliases.

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

Owner Landing likewise has no current publisher or direct consumer for its
standalone aggregate. AOST-D-0009 retires its builder, output, catalog entry,
and dedicated mechanic part while preserving both landing event kinds and
their normalization for the active Supersession Drop read model. Its schema
remains contract history and its former output remains managed cleanup.

Runtime Closeout follows the same lifecycle under AOST-D-0010. Slot 22 is
reserved by its retired tombstone, and stale runtime copies remain removable.
A future closeout surface requires a new active profile and slot, an
owner-approved canonical ABI, a real publisher, and current evidence rather
than replaying the tombstone or historical fixture.

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
- `deferred/`: bounded contract candidates whose partial owner chain,
  consumer risk, and activation gaps are emitted as caution metadata, never as
  active surfaces.
- `retired/`: cleanup/provenance tombstones for removed outputs; they carry no
  builder, generated payload, catalog entry, or active mechanic handoff. Their
  `former_catalog_order` values reserve stable slots that active profiles may
  not reuse.

Do not activate a deferred profile by moving the file alone. Its producer,
input chain, public schema/output, mechanic route, and validation must become
real in the same bounded change.

Do not reactivate a retired tombstone. Reintroduction is a new active-surface
decision with current evidence, a new reviewed slot, and consumer review.
