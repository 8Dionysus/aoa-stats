# AGENTS.md
Local guidance for `config/` in `aoa-stats`.

Read the root `AGENTS.md` first. This directory contains stats-owned intake and
event-kind configuration such as `stats_event_kind_registry.json` and
`live_receipt_sources.json`.

## Local role
Config defines what the stats layer may read and how event families are named.
It does not define owner-repo truth or live quest state.

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
python scripts/validate_repo.py
```
