# AGENTS.md
Local guidance for `generated/` in `aoa-stats`.

Read the root `AGENTS.md` first. This directory contains machine-first derived
summary surfaces built from source-owned receipts and bounded evidence refs.

## Local role
Source repos own meaning. `aoa-stats` owns derived views. Generated summaries
may illuminate movement, but they must remain weaker than owner-local source
surfaces.

## Editing posture
Do not hand-edit generated outputs. Change source receipts, schemas, or builder
logic, then regenerate. Preserve deterministic ordering, compact shape, and
explicit evidence/source references.

## Hard no
Do not turn counts, windows, or summary volume into proof of mastery, intent,
self-agency, route authority, or live quest state.

## Validation
Run:

```bash
python scripts/build_views.py --check
python scripts/validate_repo.py
python -m pytest -q tests
```
