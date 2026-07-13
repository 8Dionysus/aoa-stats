# Stats read models

This branch is the authored source body behind the public summary-surface
catalog. Each record defines one derived question, its evidence posture,
stronger-owner inputs, authority ceiling, consumer risk, public routes,
lifecycle, and mechanic handoffs.

The generated catalog projects public fields from these profiles. It is a
consumer read model, not an editable copy or status owner.

## Profile contract

`surface-profile.schema.json` constrains every source record. Importable
implementation stays under `src/aoa_stats_builder/`, public schemas stay under
`schemas/`, derived outputs stay under `generated/`, and operation payload and
focused proof stay with the mechanic parts named by `mechanic_routes`.

## Lifecycle

| State | Meaning | Must not imply |
| --- | --- | --- |
| `active/` | source profile for a public catalog surface | that committed output is current runtime state |
| `deferred/` | evidence-gated contract candidate with explicit activation gaps | an active slot, output, live selector, or promised activation |
| `retired/` | minimal cleanup and provenance tombstone | a builder, catalog entry, payload archive, or active mechanic |

`catalog_order` is a stable public slot, not a dense list position. Retired
profiles reserve `former_catalog_order`; later surfaces do not close or reuse
that gap merely for visual continuity.

Do not activate a deferred profile by moving its file. Its producer, owner
input chain, public schema/output, mechanic route, and validation must become
real together. Do not reactivate a retired tombstone; reintroduction is a new
reviewed active-surface decision with current evidence and a new reviewed slot.

## Live posture

`live_state_capable` is an executable selector. `true` permits local live
materialization only through the current refresh contract; `false` keeps the
surface on its committed/reference route and out of the live catalog.

The selector does not certify provenance. Continuously advertised state still
requires a current owner source plus an observation route that notices source
movement. Missing live input never authorizes fallback to examples or retired
defaults.

Live-refresh runtime code and part-local proof derive exact allowlist and
cleanup membership directly from the active and retired profile records. Their
mechanic guidance must describe the selection rule without copying profile
counts or a complete lifecycle roster.

## Current-state lookup

Do not maintain profile counts, named live/reference rosters, retirement
chronology, or mechanic-specific compatibility notes in this README.

Use:

- the target profile for exact current source posture
- `generated/summary_surface_catalog.min.json` for checked public discovery
- `mechanics/topology.json` and the target part for operation ownership
- `mechanics/recurrence/parts/live-receipt-refresh/` for materialization and
  stale-cleanup behavior
- `docs/decisions/README.md` indexes for boundary rationale
- Git history and changelog for chronology

## Change route

1. Read `AGENTS.md`, `surface-profile.schema.json`, and the target profile.
2. Follow every schema, output, owner-input, decision, and mechanic route it
   names.
3. Change the authored profile first.
4. Rebuild/check generated projections.
5. Run source-home, topology, focused mechanic, and public-catalog validation.

## Stop lines

- A profile owns derived meaning, not upstream facts or verdicts.
- A generated catalog does not own lifecycle.
- A committed example is not live evidence.
- A deferred gap cannot be hidden to make a candidate look active.
- A retired record cannot keep an empty mechanic alive.

## Validation

Use [`AGENTS.md#verification`](AGENTS.md#verification), then the
`VALIDATION.md` owned by every affected mechanic part.
