# AGENTS.md
Local guidance for `tests/` in `aoa-stats`.

Read the root `AGENTS.md` first. Tests protect deterministic derivation and
boundary integrity.

## Local role
Tests should prove that generated outputs, schemas, and live receipt handling
remain source-linked, derived-only, and weaker than owner-local meaning.

Keep repo-wide build fan-out, public-contract integration, and root topology
checks here. Move producer- or operation-specific invariants to the nearest
mechanic part even when the root facade keeps a compatibility alias.

## Editing posture
Prefer fixtures that expose boundary drift: ambiguous evidence refs, unknown
event kinds, stale generated output, and attempts to infer authority from counts.

## Hard no
Do not write tests that bless dashboard sovereignty, proof-by-volume, or hidden
owner-repo assumptions.

## Validation
Run:

```bash
python -m pytest -q tests mechanics
python scripts/validate_repo.py
```
