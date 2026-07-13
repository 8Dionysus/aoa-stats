# AOST-D-0008 Retired Outputs Remain Cleanup Tombstones, Not Active Stats

## Index Metadata

- Decision ID: AOST-D-0008
- Original date: 2026-07-11
- Surface classes: stats/read-models, src/catalog, mechanics/recurrence, mechanics/titan, generated/read-models, state/generated
- Stats surfaces: read-model lifecycle, summary surface catalog, live stale cleanup, Titan Summon
- Source lanes: aoa-stats authored profiles, aoa-sdk Titan swarm-ledger contract, aoa-routing consumer re-grounding
- Guard families: source-of-truth lifecycle, derived-only authority, retired-output cleanup, missing-evidence visibility, catalog-output parity, consumer handoff
- Posture: accepted

## Status

Accepted

## Context

The authored read-model source home originally distinguished only active
profiles and deferred contract candidates. Live refresh used every active
profile output name as its stale-file cleanup universe. That made removal
unsafe: deleting an active profile would also stop cleanup from removing an
older deployed copy, while retaining the profile kept a surface in the public
catalog and committed build even when it no longer deserved publication.

AOST-D-0007 corrected Titan Summon semantics by labeling its four zeros as a
`no-observed-ledger` compatibility baseline. The correction also established
that no committed owner swarm-ledger instance, closeout receipt, or real
activity observation supported the surface. Workspace-wide consumer search at
the current owner refs found only the aoa-stats publication and the derived
aoa-routing re-grounding hint; no SDK, agent, playbook, eval, memo, KAG,
profile, runtime, or abyss-stack consumer required the payload.

Keeping a content-free read model active merely to preserve cleanup would make
deployment mechanics stronger than source meaning. Deleting it without a
tombstone would leave stale `state/generated/` copies unmanaged.

## Decision

`stats/read-models/` gains a third source-owned lifecycle state:

1. `active/` profiles authorize catalog publication and build fan-out;
2. `deferred/` profiles describe contract-only candidates and activation
   conditions;
3. `retired/` profiles are minimal tombstones that authorize cleanup and
   preserve decision provenance only.

Retired records do not enter the public catalog, do not cause a builder to run,
and do not require the former committed output to exist. The managed live
cleanup inventory is derived from active output refs plus retired output refs;
the materialization allowlist remains derived only from active profiles whose
`live_state_capable` value is true. Retired names must not collide with active
or deferred names or with another managed output.

Titan Summon is the first retirement. Its active profile, root builder, pure
baseline function, build fan-out entry, committed generated payload, catalog
entry, and roadmap family entry are removed. Its v1 schema remains at the
stable root route as contract history, and a retired profile records the
former output, former mechanic route, cleanup scopes, consumer return route,
and this decision. The part-local Titan docs retain only the boundary and
reactivation conditions.

This decision supersedes the AOST-D-0007 choice to keep the no-ledger v1
baseline active for compatibility. AOST-D-0007 remains authoritative for the
facts that missing ledger evidence is not observed zero activity and that a
future observed surface requires owner-local evidence.

## Options Considered

- Keep Titan Summon active indefinitely: rejected because no source fact is
  projected and compatibility alone does not justify a catalog surface.
- Delete the profile and output without a lifecycle record: rejected because
  stale deployed copies would leave the managed cleanup universe.
- Move the old generated JSON into mechanic legacy: rejected because Git
  history already preserves the bytes and an archived payload could be
  mistaken for an active reference source.
- Publish retired entries in the v2 summary catalog: rejected because the
  catalog is an active/deferred consumer surface, not a deployment tombstone
  registry.
- Add a minimal source-home retired profile consumed only by validators and
  cleanup: chosen because it preserves operational safety without preserving
  content-free observability.

## Rationale

Source meaning must decide whether a read model exists. Generated payloads,
MCP access, routing hints, and deployed files are weaker consumers and cannot
force a source to remain active. At the same time, deletion is a lifecycle
operation: a previously managed runtime file must remain removable after its
catalog source disappears.

The tombstone is therefore active cleanup input but not active stats content.
It carries the smallest durable information needed to remove stale copies,
route consumers away, and explain the retirement. Historical payload bytes
remain discoverable in Git rather than becoming a second legacy canon.

## Consequences

- The authored inventory becomes 24 active profiles, one deferred profile,
  and one retired profile.
- Eleven active profiles remain live-admitted; thirteen active profiles remain
  committed/reference-only.
- The managed stale-cleanup universe remains 25 former-or-current output names,
  so `titan_summon_summary.min.json` is deleted if found under live state.
- The public catalog contains 24 active surfaces and no Titan Summon entry.
- `generated/titan_summon_summary.min.json` and its builder code are removed;
  `schemas/titan_summon_summary.schema.json` remains as contract history.
- The Titan mechanic keeps Incarnation projection proof and the retired Summon
  boundary, but no longer owns a static zero producer.
- `aoa-routing` must remove the retired hint after pinning the landed aoa-stats
  ref. No other current consumer handoff is required.
- A future Titan Summon projection must create a reviewed active profile from
  real owner-local ledger or closeout evidence; it may not silently reactivate
  the retired baseline.

## Source Surfaces

- `AGENTS.md`
- `DESIGN.md`
- `stats/AGENTS.md`
- `stats/read-models/AGENTS.md`
- `stats/read-models/README.md`
- `stats/read-models/surface-profile.schema.json`
- `stats/read-models/retired/titan_summon_summary.profile.json`
- `stats/source_home.manifest.json`
- `src/aoa_stats_builder/surface_catalog.py`
- `src/aoa_stats_builder/titan_observation.py`
- `scripts/build_views.py`
- `scripts/validate_stats_source_home.py`
- `mechanics/recurrence/parts/live-receipt-refresh/scripts/refresh_live_stats.py`
- `mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py`
- `mechanics/titan/parts/incarnation-summon/`
- `schemas/titan_summon_summary.schema.json`
- `generated/summary_surface_catalog.min.json`
- `aoa-routing/generated/stats_regrounding_hints.min.json`

## Validation

Decision-lane checks are owned by [`AGENTS.md#verify`](AGENTS.md#verify).
Affected source-home and mechanic checks route through their owning
`AGENTS.md` or `VALIDATION.md`, then the root
[`AGENTS.md#verify`](../../AGENTS.md#verify) gate and the release runbook.
