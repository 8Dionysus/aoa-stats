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
  (currently 16 authored profiles)
- `state/generated/summary_surface_catalog.min.json` lists only outputs
  actually admitted and materialized by that live run
- cleanup still covers every managed active output, so an older runtime copy
  of a reference-only surface is removed
- the Component Refresh, Continuity Window, Codex Plane Deployment, trusted
  rollout-history, and cadence-example adapters are never implicit live
  fallbacks

Those nine committed/reference profiles are therefore absent from live output
until explicit owner-runtime, deploy-local, or active-cadence source contracts
land. Codex Plane refresh passes an explicit `live` source mode and workspace
root so future activation cannot silently reuse committed 8Dionysus inputs. The
selector and stale-cleanup precedent is recorded for Component Refresh in
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`;
it does not decide the other eight reference-only profiles.

## Payload

- `config/live_receipt_sources.json`
- `config/live_receipt_sources.example.json`
- `docs/LIVE_SESSION_USE.md`
- `systemd/aoa-stats-live-refresh.path`
- `systemd/aoa-stats-live-refresh.service`
- `tests/`
