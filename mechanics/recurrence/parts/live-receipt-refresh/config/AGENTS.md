# AGENTS.md

## Live-receipt-refresh registry

This directory contains the active `live_receipt_sources.json` integration
registry and its operator example. The authored event-kind admission table
lives in `stats/intake-contract/event-kind-registry.json`.

When a source registration is selected, open the registry, source-family
record, and owner feed contract as needed. Config defines which owner-local
feeds the stats layer may read; it does not define event-family meaning,
owner-repo truth, or live quest state.

## Editing posture and hard no

Keep owner repository, expected feed path, event family, and boundary caveat
visible. Keep examples separate from active config. Do not register private
feeds, secret paths, or source kinds that make stats act like workflow,
proof, or route authority.

## Conditional validation

Use the live-receipt-refresh part `VALIDATION.md` for registry, publisher, and
refresh tests. Report source registration, missingness, and whether the audit
observed a current feed; a config entry alone is not live evidence.
