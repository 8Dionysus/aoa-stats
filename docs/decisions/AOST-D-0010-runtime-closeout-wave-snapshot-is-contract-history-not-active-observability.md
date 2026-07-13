# AOST-D-0010 Runtime Closeout Wave Snapshot Is Contract History, Not Active Observability

## Index Metadata

- Decision ID: AOST-D-0010
- Original date: 2026-07-11
- Surface classes: stats/read-models, mechanics/checkpoint, src/projection, generated/read-models, state/generated
- Stats surfaces: Runtime Closeout, read-model lifecycle, stable catalog slots, live stale cleanup
- Source lanes: abyss-stack runtime trial closeouts, historical abyss-stack wave receipts, aoa-sdk runtime return transport, aoa-routing consumer re-grounding
- Guard families: source-of-truth lifecycle, derived-only authority, owner-contract compatibility, retired-slot reservation, retired-output cleanup, mechanic topology, catalog-output parity, consumer handoff
- Posture: accepted

## Status

Accepted

## Context

AOST-D-0006 corrected Runtime Closeout from a false live claim to an honest
committed compatibility snapshot. It preserved the historical
`runtime_wave_closeout_receipt` projection while proving that the current
`abyss-stack` producer and the `aoa-sdk` transport use different contracts.
That correction was necessary, but it did not answer whether the standalone
read model still deserved an active catalog position.

The follow-up necessity audit checked the current owner and consumer graph.
At `abyss-stack@78814b3`, local trials publish
`runtime_trial_closeout_receipt`, not the historical wave payload. At
`aoa-sdk@cf29944`, `build_runtime_wave_closeout_receipt` is only a public name
compatibility alias: it delegates to `build_runtime_return_closeout_receipt`
and emits `runtime_return_closeout_receipt`. Neither current contract carries
the `program_id` plus `wave_id` ABI projected by the stats surface.

No current owner publishes the historical wave contract to an admitted live
source. No active external consumer reads the Runtime Closeout payload. The
only current exact surface-name consumer is the derived aoa-routing
re-grounding hint; older Dionysus ecosystem-audit references record the
historical rollout rather than a current dependency. The committed summary is
therefore a replay of one bounded historical fixture, not a current owner
observation or a required compatibility product.

The historical receipt itself still carries useful generic evidence. Object,
Repeated Window, and Source Coverage consume the common envelope without
claiming a dedicated closeout projection. Retirement of Runtime Closeout must
not delete that fixture, event-kind admission, or generic observation value.

## Decision

Runtime Closeout leaves active publication. Its active profile, deterministic
builder, package export, root build facade aliases and fan-out, committed
payload, catalog entry, focused producer tests, and repo-local Checkpoint
mechanic package are removed.

A minimal retired profile reserves former catalog slot 22 and keeps
`generated/runtime_closeout_summary.min.json` in the managed stale-cleanup
universe. The root schema remains as contract history. The retired mechanic
route is provenance only and does not require an empty `mechanics/checkpoint/`
package to remain in the live tree.

`runtime_wave_closeout_receipt` remains an active compatibility event kind for
`object_summary`, `repeated_window_summary`, and `source_coverage_summary`.
The bounded fixture remains admitted. It no longer names the retired Runtime
Closeout surface as a consumer.

This decision supersedes the AOST-D-0006 choice to retain Runtime Closeout as
an active committed compatibility surface. AOST-D-0006 remains authoritative
for the stronger rule that `runtime_wave_closeout_receipt`,
`runtime_trial_closeout_receipt`, and `runtime_return_closeout_receipt` are
distinct contracts and must not be implicitly aliased.

## Options Considered

- Keep the historical wave summary active indefinitely: rejected because a
  single fixture replay without a current publisher or direct consumer does
  not justify active observability.
- Adapt current trial or return receipts into the wave projection: rejected
  because no owner contract declares those payloads equivalent.
- Delete the wave event kind and fixture with the surface: rejected because
  the historical receipt remains valid generic intake evidence for active
  observation summaries.
- Keep an empty Checkpoint package as a retirement marker: rejected because
  the tombstone, decision record, and Git history already preserve provenance,
  while an empty package would overstate current local capability.
- Retire only the standalone projection while preserving ABI history, generic
  intake, stable slot identity, and cleanup: chosen because it removes
  unsupported product surface without erasing useful evidence vocabulary.

## Rationale

An importable builder and stable bytes prove determinism, not necessity.
Source meaning and a real consumer graph decide whether a public stats read
model belongs in the active catalog. A routing hint is downstream advisory
material and cannot keep its source alive after the owner and direct-consumer
contracts disappear.

The split between receipt admission and summary lifecycle prevents an
over-broad deletion. The historical wave receipt can still contribute to
generic object, activity-window, and coverage observations without claiming
that aoa-stats owns a current runtime closeout product.

Removing the last active part also removes the repo-local Checkpoint package.
The common Checkpoint center remains authoritative in `Agents-of-Abyss`; this
repository should expose that mechanic only when it owns a real repeatable
stats operation below it.

## Consequences

- The authored inventory becomes 22 active profiles, one deferred profile,
  and three retired profiles.
- Eleven active profiles remain live-admitted and eleven active profiles
  remain committed/reference-only.
- The managed stale-cleanup universe remains 25 output names: 22 active plus
  three retired tombstones.
- Active catalog slots are 1-3, 5-20, and 23-25; retired slots 4, 21, and 22
  remain reserved.
- `generated/runtime_closeout_summary.min.json` and its builder disappear,
  while `schemas/runtime-closeout-summary.schema.json` remains contract
  history.
- The historical wave receipt remains in the intake fixture and continues to
  feed Object, Repeated Window, and Source Coverage.
- `mechanics/checkpoint/` leaves the active topology because it has no
  remaining local operation.
- Live refresh continues to delete stale Runtime Closeout, Owner Landing, and
  Titan Summon files.
- `aoa-routing` must remove the Runtime Closeout hint after pinning this landed
  aoa-stats ref. No other current direct consumer handoff is required.
- A future runtime closeout projection requires a new reviewed active profile,
  a new slot, an owner-approved canonical ABI, a real publisher, current
  evidence, and an observation route when live admission is claimed. It may
  not reactivate slot 22 by copying the tombstone.

## Source Surfaces

- `AGENTS.md`
- `DESIGN.md`
- `stats/AGENTS.md`
- `stats/read-models/AGENTS.md`
- `stats/read-models/README.md`
- `stats/read-models/retired/runtime_closeout_summary.profile.json`
- `stats/intake-contract/event-kind-registry.json`
- `stats/intake-contract/examples/session_harvest_family.receipts.example.json`
- `stats/source_home.manifest.json`
- `mechanics/topology.json`
- `mechanics/recurrence/parts/live-receipt-refresh/`
- `schemas/runtime-closeout-summary.schema.json`
- `generated/summary_surface_catalog.min.json`
- `aoa-routing/generated/stats_regrounding_hints.min.json`

## Validation

Decision-lane checks are owned by [`AGENTS.md#verify`](AGENTS.md#verify).
Affected source-home and mechanic checks route through their owning
`AGENTS.md` or `VALIDATION.md`, then the root
[`AGENTS.md#verify`](../../AGENTS.md#verify) gate and the release runbook.
