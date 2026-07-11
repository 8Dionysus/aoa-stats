# AGENTS.md
Local guidance for the live-receipt-refresh registry.

Read the repository root and recurrence route cards first. This directory
contains the active `live_receipt_sources.json` integration registry and its
operator example. The authored event-kind admission table lives at
`stats/intake-contract/event-kind-registry.json`.

## Local role
Config defines which owner-local feeds the stats layer may read. It does not
define event-family meaning, owner-repo truth, or live quest state.

## Editing posture
Keep source ownership visible. When adding a live receipt source, name the owner
repo, expected feed path, event family, and boundary caveat. Keep examples
separate from active config.

## Hard no
Do not register private feeds, secret paths, or source kinds that make stats act
like workflow authority, proof authority, or route authority.

## Validation
Run:

```bash
python scripts/check_live_publishers.py
python -m pytest -q mechanics/recurrence/parts/live-receipt-refresh/tests
```
