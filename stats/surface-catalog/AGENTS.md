# AGENTS.md

Route card for the `surface-catalog` stats source family.

## Ownership

This family owns the catalog entry shape, surface profile vocabulary, and the
authority ceiling attached to each committed derived summary surface.

It does not own the owner-local facts, receipts, verdicts, route state, memory,
or runtime truth summarized by those surfaces. A catalog entry is a bounded
description and discovery route, not proof that the underlying source is
complete or current.

## Current source and public routes

- `docs/ARCHITECTURE.md`
- `stats/surface-catalog/SURFACE_STRENGTH_MODEL.md`
- `stats/read-models/active/`
- `stats/read-models/deferred/`
- `stats/read-models/surface-profile.schema.json`
- `stats/surface-catalog/CONSUMER_REGROUNDING.md`
- `schemas/summary-surface-catalog.schema.json`
- `generated/summary_surface_catalog.min.json`
- `manifests/artifact_bundles/summary_surface_catalog.bundle.json`

The schema and generated catalog remain active root public surfaces. Do not
copy either payload under this directory.

## Implementation, validation, and access

- implementation: `src/aoa_stats_builder/surface_catalog.py` and
  `scripts/build_views.py`
- validation: `tests/test_summary_surface_catalog.py` and the existing
  `scripts/build_views.py --check` route
- current read-only access: `stats/surface-catalog/CODEX_MCP.md`,
  `scripts/aoa_stats_mcp_server.py`, `src/aoa_stats_mcp/repo_state.py`, and
  `src/aoa_stats_mcp/server.py`
- access validation: `tests/test_aoa_stats_mcp_state.py`

## Mechanics crosswalk

- `mechanics/recurrence/parts/component-manifests`
- `mechanics/boundary-bridge/parts/consumer-regrounding`

The recurrence part owns component recurrence-manifest operation posture. The
boundary bridge part owns the consumer handoff back to stronger owner
surfaces. Neither part may strengthen a catalog entry's authority.

## Change law

- Every catalog entry keeps a source ref, schema ref, input posture,
  owner-truth inputs, authority ceiling, consumer risk, and live-state posture.
- `SURFACE_STRENGTH_MODEL.md` owns the closed human vocabulary used by active
  and deferred profiles. Add or remove a posture class there with profile and
  catalog proof; do not preserve unused classes or named current-surface state.
- Generated catalog changes come from authored profiles and the deterministic
  builder; do not edit the output or reintroduce an in-code specification
  table as source.
- Keep `docs/ARCHITECTURE.md` as the stable public derived-view contract. Exact
  lifecycle state and named surface posture stay in profiles, the generated
  catalog, and indexed decisions rather than being copied into that document.
- High-risk or thin-input surfaces must continue to route consumers back to
  stronger owner-local evidence.
- Keep the MCP read-only and derived-only when catalog access changes.

## Verify

```bash
python scripts/build_views.py --check
python -m pytest -q tests/test_summary_surface_catalog.py tests/test_aoa_stats_mcp_state.py
```
