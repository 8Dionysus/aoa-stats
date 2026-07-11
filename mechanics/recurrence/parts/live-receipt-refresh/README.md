# Live receipt refresh

This part routes the bounded loop that audits registered owner-local receipt
publishers, combines valid receipts into a local feed, and rebuilds deterministic
stats views.

## Status

- mechanic: `recurrence`
- stats source family: `intake_contract`
- payload route: `part_localized`
- active contract: `CONTRACT.md`
- validation route: `VALIDATION.md`

The source registry, watcher templates, operator guide, and focused tests are
part-local. Public compatibility commands remain at root `scripts/` and load
the canonical assets from this part.

## Payload

- `config/live_receipt_sources.json`
- `config/live_receipt_sources.example.json`
- `docs/LIVE_SESSION_USE.md`
- `systemd/aoa-stats-live-refresh.path`
- `systemd/aoa-stats-live-refresh.service`
- `tests/`
