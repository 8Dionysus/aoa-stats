# AGENTS.md

## Applies to

This card applies to `aoa-stats/kag/` and every nested path until a nearer card
narrows the lane.

## Role

`kag/` is the local KAG provider home for `aoa-stats`. It exposes compact,
source-linked records over derived observability registries and stats route
surfaces for `aoa-kag` registry, composition, and MCP consumers.

## Read before editing

Read the root `AGENTS.md`, this card, `kag/README.md`, `kag/manifest.json`,
`README.md`, `docs/BOUNDARIES.md`, `generated/summary_surface_catalog.min.json`,
and `generated/agon_kag_stats_observability_registry.min.json` before changing
provider records.

## Boundaries

Keep derived observability posture with `aoa-stats` and source-owner claims with
the repositories that emitted the receipts, refs, or verdicts. Keep shared KAG
schema, registry, composition, and provider validation with `aoa-kag`. Keep
runtime serving state with `abyss-stack` or the runtime owner named by the
consumer.

## Validation

Use the owner validator named in `manifest.json`, then validate this provider
through the `aoa-kag` local subtree validator.

## Closeout

Report provider records changed, source-return route changed, owner validation,
`aoa-kag` validation, and the next MCP consumer route.
