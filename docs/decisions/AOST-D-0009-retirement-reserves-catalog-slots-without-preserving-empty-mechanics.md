# AOST-D-0009 Retirement Reserves Catalog Slots Without Preserving Empty Mechanics

## Index Metadata

- Decision ID: AOST-D-0009
- Original date: 2026-07-11
- Surface classes: stats/read-models, src/catalog, mechanics/method-growth, mechanics/recurrence, generated/read-models, state/generated
- Stats surfaces: read-model lifecycle, stable catalog slots, Owner Landing, Supersession Drop, live stale cleanup
- Source lanes: aoa-stats authored profiles, aoa-skills reviewed landing bundles, Dionysus seed landing traces, aoa-routing consumer re-grounding
- Guard families: source-of-truth lifecycle, derived-only authority, retired-slot reservation, retired-output cleanup, mechanic topology, catalog-output parity, consumer handoff
- Posture: accepted

## Status

Accepted

## Context

AOST-D-0008 introduced retired read-model tombstones while removing the
unsupported Titan Summon surface. That landing preserved stale-output cleanup,
but it also renumbered every later active `catalog_order` to keep the active
sequence dense. A dense ordinal makes unrelated profiles change identity when
one earlier surface retires and leaves no machine-readable record of the
former catalog position.

The next necessity audit examined all thirteen reference-only active surfaces
at current owner-repository refs. `owner_landing_summary` was the weakest
remaining active surface: no current owner-local publisher emits
`reviewed_owner_landing_receipt` or `seed_owner_landing_trace_receipt`, no
current direct consumer requires the standalone payload, and its committed
output merely replays the aoa-stats intake example. The only external exact
surface-name consumer was the derived aoa-routing re-grounding hint. The
historical Dionysus planting report records the original cross-repo landing but
explicitly routes future work back to live owner repositories.

The landing receipt vocabulary is not wholly dead. The active
`supersession_drop_summary` consumes explicit supersede, merge, drop, and
reanchor fields from those receipt kinds. Retiring their standalone aggregate
must not remove that shared input ABI or normalization.

## Decision

`catalog_order` is a stable catalog slot, not a dense active-list position.
Every retired profile records a positive `former_catalog_order`; active slots
and retired slots must be globally unique. Retirement leaves a reserved gap,
and later active profiles are not renumbered merely to close it. Titan Summon
reserves its original slot 21, Owner Landing reserves slot 4, and the four
profiles that followed Titan return to their original slots 22 through 25.

Owner Landing leaves active publication. Its active profile, standalone
builder and export, build fan-out, committed payload, catalog entry, dedicated
example, and dedicated active mechanic part are removed. Its schema remains at
the stable root path as contract history, and its retired profile keeps the
former output in managed stale cleanup. The two landing event kinds,
normalizers, and focused turnover tests remain because Supersession Drop still
consumes them.

`former_mechanic_routes` is retirement provenance, not an active topology
backlink. A retired profile may name a path that exists only in Git history; it
must not force an empty mechanic part to remain in the live tree. Active and
deferred profiles continue to require exact reciprocal links to active
mechanic parts.

This decision supersedes the AOST-D-0004 choice to keep Owner Landing as an
active reference-only contract snapshot. AOST-D-0004 remains authoritative for
the general rule that live admission requires both a current source and an
observation route, and for the still-active Memory Movement and Stress Recovery
cases.

## Options Considered

- Keep Owner Landing as a reference-only example surface: rejected because a
  self-authored fixture without a current publisher or direct consumer is
  contract demonstration, not necessary observability.
- Remove the landing event kinds and all normalization: rejected because
  Supersession Drop still derives explicit turnover from those inputs.
- Retire the surface but densely renumber later profiles again: rejected
  because lifecycle cleanup should not mutate unrelated catalog identities.
- Keep the dedicated mechanic part as a retirement marker: rejected because
  retired source profiles and Git history already carry provenance, while an
  inactive operation shell would overstate current capability.
- Reserve former slots in retirement tombstones and keep only actively
  consumed Method Growth logic: chosen because it preserves identity, cleanup,
  and useful ABI while reducing false active surface area.

## Rationale

Source meaning decides whether a stats projection deserves to exist. A schema
may remain useful as contract history and receipt types may remain useful to a
different projection without justifying a standalone generated read model.
Separating those concerns lets `aoa-stats` remove overcode at the precise
boundary instead of deleting shared evidence vocabulary or preserving an
example-only dashboard surface.

Stable slots also make lifecycle changes local. Catalog consumers do not see
`catalog_order`, but source profiles and future migrations do. Reserving former
slots prevents accidental reuse and makes the authored history mechanically
checkable without publishing retired entries in the public catalog.

## Consequences

- The authored inventory becomes 23 active profiles, one deferred profile,
  and two retired profiles.
- Eleven active profiles remain live-admitted and twelve active profiles remain
  committed/reference-only.
- The managed stale-cleanup universe remains 25 output names: 23 active plus
  two retired tombstones.
- Active catalog slots are 1-3, 5-20, and 22-25; retired slots 4 and 21 remain
  reserved and cannot be reused.
- `generated/owner_landing_summary.min.json` and its builder disappear, while
  `schemas/owner-landing-summary.schema.json` remains contract history.
- Method Growth has two active parts: Candidate Lineage and Supersession
  Pruning. Landing receipt normalization remains in the shared core only as an
  input to explicit turnover.
- Live refresh continues to remove stale Owner Landing and Titan Summon files.
- `aoa-routing` must remove the retired Owner Landing hint after pinning the
  landed aoa-stats ref. No other current direct consumer handoff is required.
- A future standalone Owner Landing projection requires a new reviewed active
  profile, a new slot, a real owner publisher, current receipts, and an
  observable refresh or explicit committed-reference contract. It may not
  reactivate slot 4 by copying the tombstone.

## Source Surfaces

- `AGENTS.md`
- `DESIGN.md`
- `stats/AGENTS.md`
- `stats/read-models/AGENTS.md`
- `stats/read-models/README.md`
- `stats/read-models/surface-profile.schema.json`
- `stats/read-models/retired/owner_landing_summary.profile.json`
- `stats/read-models/retired/titan_summon_summary.profile.json`
- `stats/source_home.manifest.json`
- `src/aoa_stats_builder/surface_catalog.py`
- `src/aoa_stats_builder/candidate_lifecycle.py`
- `mechanics/method-growth/`
- `mechanics/recurrence/parts/live-receipt-refresh/`
- `schemas/owner-landing-summary.schema.json`
- `generated/summary_surface_catalog.min.json`
- `aoa-routing/generated/stats_regrounding_hints.min.json`

## Validation

Decision-lane checks are owned by [`AGENTS.md#verify`](AGENTS.md#verify).
Affected source-home and mechanic checks route through their owning
`AGENTS.md` or `VALIDATION.md`, then the root
[`AGENTS.md#verify`](../../AGENTS.md#verify) gate and the release runbook.
