# Component refresh contract

## Purpose

Produce a deterministic, derived-only committed reference model from the
reviewed `aoa-sdk` Component Refresh examples while preserving owner-local
refresh artifacts and validation as the stronger truth.

## Inputs

- the authored `component_refresh_summary` profile under `stats/read-models/`
- the reviewed `aoa-sdk` drift-hint and followthrough-decision examples loaded
  by `src/aoa_stats_builder/component_refresh_sources.py`
- this part's refresh guide and examples

The live receipt registry is not an input to this reference surface. Its
receipt feed does not contain a Component Refresh owner-runtime chain.

## Output

`generated/component_refresh_summary.min.json`, a committed reference snapshot
validated by `schemas/component-refresh-summary.schema.json`.

## Adapter boundary

- `component_refresh_sources.py` owns filesystem discovery, JSON loading, and
  construction of the immutable reviewed-example bundle.
- filesystem-free `component_refresh.py` owns reference packet validation and
  deterministic projection; its projection receives the validated bundle.
- `scripts/build_views.py` preserves the zero-argument compatibility facade for
  the committed build.
- live refresh supplies no Component Refresh bundle and must not fall back to
  examples, owner laws, or inferred owner state.

## Invariants

- the summary may describe refresh posture but cannot prove refresh success
- reference examples never become current state because a live command ran
- decision-only components do not borrow freshness from unrelated hints
- owner-local validation, receipts, and rollback anchors outrank the summary
- no hidden scheduler or cross-repo maintenance authority is implied

## Future live activation

Live activation requires a canonical owner-runtime artifact that preserves the
reviewed chain from drift hint through followthrough decision to an owner-local
`component_refresh_receipt`. That source contract, its validation, and the
profile activation change must land explicitly; adding the artifact to the
shared receipt ABI is a separate owner decision.

## Crosswalk

This part operates on stats source-family id `read_models`. The source profile
owns meaning; this part owns repeatable refresh-summary operation posture.
The reference/live split is recorded in
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`.
