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
  universe: currently 25 read models
- only profiles with `live_state_capable: true` enter the live build allowlist
  (currently 11 authored profiles)
- `state/generated/summary_surface_catalog.min.json` lists only outputs
  actually admitted and materialized by that live run
- cleanup still covers every managed active output, so an older runtime copy
  of a reference-only surface is removed
- the Component Refresh, Continuity Window, Codex Plane Deployment, Memory
  Movement, Route Progression, Runtime Closeout, Stress Recovery, trusted
  rollout-history, and cadence-example adapters are never implicit live
  fallbacks

All 14 committed/reference profiles are therefore absent from live output
until both their current owner source and the observation route that can cause
refresh are real. Owner Landing and Stress Recovery still lack their named
owner publishers. Memory Movement reads a real reviewed `aoa-memo` corpus,
but the watcher does not observe changes to its catalog, object, reviewed
intake, or landing-receipt roots; the memo writeback receipt log is not a
substitute for that missing corpus trigger.

The active registry excludes the historical runtime-wave log. Current
`abyss-stack` trial receipts and SDK return receipts have distinct contracts;
neither is admitted as a wave alias. AOST-D-0006 records the reactivation gate.

Codex Plane refresh passes an explicit `live` source mode and workspace root
so future activation cannot silently reuse committed 8Dionysus inputs. The
selector and stale-cleanup precedent is recorded for Component Refresh in
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`.
The current-source plus observation law, including the three newly closed
selectors, is recorded in
`docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md`.

## Payload

- `config/live_receipt_sources.json`
- `config/live_receipt_sources.example.json`
- `docs/LIVE_SESSION_USE.md`
- `systemd/aoa-stats-live-refresh.path`
- `systemd/aoa-stats-live-refresh.service`
- `tests/`
