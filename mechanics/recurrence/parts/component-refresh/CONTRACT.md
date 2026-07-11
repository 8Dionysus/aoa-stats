# Component refresh contract

## Purpose

Produce a deterministic, derived-only read model of reviewed component refresh
posture while preserving owner-local refresh decisions and validation as the
stronger truth.

## Inputs

- the authored `component_refresh_summary` profile under `stats/read-models/`
- reviewed owner hints and followthrough decisions consumed by the shared
  builder
- this part's refresh guide and examples
- the live receipt registry only where the owner law names it as a source

## Output

`generated/component_refresh_summary.min.json`, validated by
`schemas/component-refresh-summary.schema.json`.

## Invariants

- the summary may describe refresh posture but cannot prove refresh success
- decision-only components do not borrow freshness from unrelated hints
- owner-local validation, receipts, and rollback anchors outrank the summary
- no hidden scheduler or cross-repo maintenance authority is implied

## Crosswalk

This part operates on stats source-family id `read_models`. The source profile
owns meaning; this part owns repeatable refresh-summary operation posture.
