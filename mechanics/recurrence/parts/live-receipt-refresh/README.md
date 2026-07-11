# Live receipt refresh

This part routes the bounded loop that audits registered owner-local receipt
publishers, combines valid receipts into a local feed, and materializes only
the deterministic stats views admitted for live state by their authored
profiles.

## Status

- mechanic: `recurrence`
- stats source family: `intake_contract`
- payload route: `part_localized`
- active contract: `CONTRACT.md`
- validation route: `VALIDATION.md`

The source registry, watcher templates, operator guide, and focused tests are
part-local. Public compatibility commands remain at root `scripts/` and load
the canonical assets from this part.

## Live inventory contract

- active profiles under `stats/read-models/active/` define the managed output
  universe
- only profiles with `live_state_capable: true` enter the live build allowlist
- `state/generated/summary_surface_catalog.min.json` lists only outputs
  actually admitted and materialized by that live run
- cleanup still covers every managed active output, so an older runtime copy
  of a reference-only surface is removed
- the Component Refresh reviewed-example adapter is never an implicit live
  fallback

The Component Refresh committed reference profile is therefore absent from
live output until an explicit owner-runtime source contract lands. See
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`.

## Payload

- `config/live_receipt_sources.json`
- `config/live_receipt_sources.example.json`
- `docs/LIVE_SESSION_USE.md`
- `systemd/aoa-stats-live-refresh.path`
- `systemd/aoa-stats-live-refresh.service`
- `tests/`
