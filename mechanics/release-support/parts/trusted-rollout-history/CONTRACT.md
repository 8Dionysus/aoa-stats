# Trusted Rollout History contract

## Purpose

Produce deterministic operations and drift companions from one coherent,
checked-in owner-history bundle without calling its latest row live workspace
state.

## Exact inputs

The committed-history adapter reads only:

- `8Dionysus/generated/codex/rollout/deploy_history.jsonl`
- `8Dionysus/generated/codex/rollout/regeneration_campaigns.min.json`
- `8Dionysus/generated/codex/rollout/rollback_windows.min.json`
- `8Dionysus/generated/codex/rollout/rollout_latest.min.json`

The bundle does not read the deploy-local Codex Plane trio or the separate
campaign cadence examples.

## Adapter boundary

- `codex_trusted_rollout_sources.py` owns exact path selection, JSON/JSONL I/O,
  immutable input bundles, and checked-in source provenance
- filesystem-free `codex_trusted_rollout.py` owns lifecycle grammar, reference
  coherence, timestamp validation, and deterministic projection
- `scripts/build_views.py` retains default-owner resolution, the historical
  mutable tuple functions, zero-argument builders, the missing-latest-ref
  fallback, and repo-wide fan-out only

## Invariants

- history is non-empty and every entry keeps the published schema version
- rollout, deploy, drift, and rollback references keep their published grammar
  and one rollout suffix within each history entry
- rollout and drift states stay inside the owner lifecycle vocabularies
- boolean projection fields are actual booleans; strings cannot become truthy
- regeneration campaigns cover exactly the history campaign references
- rollback windows cover exactly the rollback references named by history
- `rollout_latest` points to the final history entry and repeats its state
- the pure core rejects a missing or unresolved latest pointer; only the root
  compatibility helper may select the last row when the pointer is absent
- the latest stable reference resolves to a stabilized history entry
- canonical source references and parseable owner timestamps remain visible
- the public output schemas and byte shape stay unchanged

## Authority and live boundary

These read models are weaker than the source-owned history and rollback
windows. Both authored profiles are reference-only. Local live refresh must
omit them and remove stale managed copies instead of replaying the committed
history under `state/generated/`.

The result never authorizes deployment, rollout, repair, stabilization, or
rollback.
