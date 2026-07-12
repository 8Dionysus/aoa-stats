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

## Profile-derived live inventory contract

- active profiles plus retired tombstones under `stats/read-models/` define the
  managed stale-cleanup universe
- only profiles with `live_state_capable: true` enter the live build allowlist
- `state/generated/summary_surface_catalog.min.json` lists only outputs
  actually admitted and materialized by that live run
- cleanup still covers every managed active output, so an older runtime copy
  of a reference-only surface is removed
- an active reference-only adapter and a retired builder are never implicit
  live fallbacks

Exact membership and counts are read from `stats/read-models/active/` and
`stats/read-models/retired/`; this part does not maintain a second roster.
Part-local tests load those source records independently and prove the live,
reference-only cleanup, and retired cleanup partitions against the refresh
implementation.

The active registry excludes the historical runtime-wave log. Current
`abyss-stack` trial receipts and SDK return receipts have distinct contracts;
neither is admitted as a wave alias. AOST-D-0006 records the ABI boundary and
AOST-D-0010 records the standalone surface retirement.

Codex Plane refresh passes an explicit `live` source mode and workspace root
so future activation cannot silently reuse committed 8Dionysus inputs. The
selector and stale-cleanup precedent is recorded for Component Refresh in
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`.
The current-source plus observation law, including the three newly closed
selectors, is recorded in
`docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md`.
Owner Landing's subsequent retirement is recorded in AOST-D-0009.
Runtime Closeout's subsequent retirement is recorded in AOST-D-0010.

## Payload

- `config/live_receipt_sources.json`
- `config/live_receipt_sources.example.json`
- `docs/LIVE_SESSION_USE.md`
- `systemd/aoa-stats-live-refresh.path`
- `systemd/aoa-stats-live-refresh.service`
- `tests/`
