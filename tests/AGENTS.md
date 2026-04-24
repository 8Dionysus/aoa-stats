# AGENTS.md
Local guidance for `tests/` in `aoa-stats`.

Read the root `AGENTS.md` first. Tests protect deterministic derivation and
boundary integrity.

## Local role
Tests should prove that generated outputs, schemas, and live receipt handling
remain source-linked, derived-only, and weaker than owner-local meaning.

## Editing posture
Prefer fixtures that expose boundary drift: ambiguous evidence refs, unknown
event kinds, stale generated output, and attempts to infer authority from counts.

## Hard no
Do not write tests that bless dashboard sovereignty, proof-by-volume, or hidden
owner-repo assumptions.

## Validation
Run:

```bash
python -m pytest -q tests
python scripts/validate_repo.py
```
