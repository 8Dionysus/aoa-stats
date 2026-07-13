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

Root fan-out proof derives expected public output names from authored profiles
and compares complete outputs with their committed bytes. It must not replay
part-owned field values, counts, or example semantics as a second test suite.
The same boundary applies to consumers and release operations: owner-return
routes and artifact trust lifecycles are proved by their Boundary Bridge and
Release Support parts, not by the root catalog-contract test.

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
