# Surface catalog

This source family defines the compact profile used to discover committed
`aoa-stats` summary surfaces without mistaking them for their stronger source
owners.

Each catalog entry names the question answered, derivation posture, owner
inputs, authority ceiling, consumer risk, and whether a live refresh can
update the surface. The generated catalog is rebuilt from authored profiles
under `stats/read-models/` and validated against its root schema.

## Active route map

| Concern | Current route |
| --- | --- |
| Derived-view architecture | `docs/ARCHITECTURE.md` |
| Surface strength vocabulary | `docs/SURFACE_STRENGTH_MODEL.md` |
| Consumer return-to-owner signals | `stats/surface-catalog/CONSUMER_REGROUNDING.md` |
| Catalog schema | `schemas/summary-surface-catalog.schema.json` |
| Authored surface profiles | `stats/read-models/active/`, `stats/read-models/deferred/` |
| Profile source schema | `stats/read-models/surface-profile.schema.json` |
| Profile loader and public projection | `src/aoa_stats_builder/surface_catalog.py` |
| Deterministic builder | `scripts/build_views.py` |
| Committed public catalog | `generated/summary_surface_catalog.min.json` |
| Public artifact bundle | `manifests/artifact_bundles/summary_surface_catalog.bundle.json` |
| Read-only access contract | `stats/surface-catalog/CODEX_MCP.md` |

## Operation crosswalk

- component recurrence inventory:
  `mechanics/recurrence/parts/component-manifests`
- consumer return to stronger owner surfaces:
  `mechanics/boundary-bridge/parts/consumer-regrounding`

The current MCP reads the generated catalog and catalog-listed surfaces. It is
an access route only; source meaning stays in this family and the root routes
listed above.

The authoritative machine-readable mapping is
`stats/source_home.manifest.json`.
