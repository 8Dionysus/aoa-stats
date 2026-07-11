# AGENTS.md

## Applies to

This card applies to `aoa-stats/kag/` and every nested path until a nearer card
narrows the lane.

## Role

`kag/` is the local KAG provider home for `aoa-stats`. It exposes compact,
source-linked records over the authored stats source home, with generated
catalogs and Agon observability kept as supporting projections for `aoa-kag`
registry, composition, and MCP consumers.

## Read before editing

Read the root `AGENTS.md`, this card, `kag/README.md`, `kag/manifest.json`,
`stats/source_home.manifest.json`, `stats/README.md`,
`stats/read-models/README.md`, `README.md`,
`generated/summary_surface_catalog.min.json`, and
`generated/agon_kag_stats_observability_registry.min.json` before changing
provider records.

## Boundaries

Keep authored stats meaning and authority ceilings in `stats/`. Keep generated
catalog and Agon observability surfaces weaker than that authored source and
weaker than the repositories that emitted the receipts, refs, or verdicts.
Keep shared KAG schema, registry, composition, and provider validation with
`aoa-kag`. Keep runtime serving state with `abyss-stack` or the runtime owner
named by the consumer.

Every provider record uses `stats/source_home.manifest.json` as its freshness
anchor. `stats/README.md` is the return route for stats-authored meaning;
`README.md` remains the explicit repository entry route.

## Validation

Use the source-home, catalog, and part-local Agon validation routes named in
`manifest.json`, then validate this provider through the `aoa-kag` local
subtree validator.

## Closeout

Report provider records changed, both source-return routes, owner validation,
`aoa-kag` validation, and the next MCP consumer route.
