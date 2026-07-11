# Recurrence provenance

## Common mechanic

The parent mechanic is `Agents-of-Abyss/mechanics/recurrence`. This package
records only the `aoa-stats` operation routes evidenced by the current
repository.

## Active localized payload

- `live-receipt-refresh` now owns the live source registry, operator guide,
  watcher templates, and focused tests. Root `scripts/` commands remain stable
  compatibility entrypoints and resolve those part-local assets.
- `component-manifests` now owns the recurrence component/hook declarations,
  projection schema and example, and recurrence boundary notes.
- `component-refresh` owns its operation guide, examples, and focused tests.
  Its importable implementation is split between the filesystem-free
  `src/aoa_stats_builder/component_refresh.py` projection and the committed
  reviewed-example adapter in
  `src/aoa_stats_builder/component_refresh_sources.py`.
- `continuity-window` owns its operation guide, example, and focused tests. Its
  importable implementation is split between filesystem-free validation and
  projection in `src/aoa_stats_builder/continuity_window.py` and the committed
  cross-owner reference adapter in
  `src/aoa_stats_builder/continuity_window_sources.py`.
- `repeated-window` has no private payload to localize in this slice: its
  schema and generated summary are intentional root public contracts, and the
  deterministic builder is shared by the read-model family.

Git rename history is the content ledger for former root routes. No legacy
copy is active.

## Reference and live split

The Component Refresh output remains a committed public reference snapshot,
but its authored profile is not live-capable. The live refresh operation
derives its materialization allowlist from active profiles, publishes a catalog
only for outputs actually materialized, and keeps the full managed profile set
as its stale-file cleanup universe. This prevents former fixture replays under
`state/generated/` from surviving as apparent current state.

The accepted rationale is
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`.

Continuity Window applies that selector precedent through its own part contract
without widening the component-specific decision. Its committed example chain
is reference-only, `continuity_status` does not prove reanchor occurrence, and
future live activation requires a separate owner-runtime continuity source.

## Public compatibility exceptions

Published read-model schemas and generated outputs remain under root
`schemas/` and `generated/`. The three live refresh commands remain under root
`scripts/`. These routes are public contracts or shared entrypoints, not a
return of operation ownership to flat root districts.

## Source-family crosswalk

- `live-receipt-refresh` ↔ `stats` family `intake_contract`
- `component-manifests` ↔ `stats` family `surface_catalog`
- `component-refresh` ↔ `stats` family `read_models`
- `continuity-window` ↔ `stats` family `read_models`
- `repeated-window` ↔ `stats` family `read_models`
