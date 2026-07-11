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
- `component-refresh` now owns its operation guide, examples, and focused test.
- `continuity-window` now owns its operation guide and example.
- `repeated-window` has no private payload to localize in this slice: its
  schema and generated summary are intentional root public contracts, and the
  deterministic builder is shared by the read-model family.

Git rename history is the content ledger for former root routes. No legacy
copy is active.

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
