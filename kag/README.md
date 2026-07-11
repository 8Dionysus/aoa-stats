# aoa-stats Local KAG Provider

`kag/` exposes the current `aoa-stats` KAG provider packet as portable
source-linked records. The authored stats source home is primary; generated
catalogs are supporting read models and never replace authored meaning.

## Operating Card

| Field | Route |
| --- | --- |
| role | local KAG provider for authored stats source meaning plus supporting derived projections |
| records | `nodes/`, `edges/`, `indexes/`, `projections/`, `receipts/` |
| manifest | `manifest.json` |
| primary source | `stats/source_home.manifest.json` |
| authored support | `stats/read-models/README.md` |
| derived support | `generated/summary_surface_catalog.min.json` |
| Agon support | `generated/agon_kag_stats_observability_registry.min.json` |
| consumer route | `aoa-kag` registry/composition, `abyss-stack`, MCP resources |
| owner return | `stats/README.md` for authored stats meaning; `README.md` for repository entry and wider context |

## Record Classes

| Class | Current record |
| --- | --- |
| node | authored source-home surface and owner-return route |
| edge | source home returns to the stats and repository routes |
| index | source surface inventory over local records |
| projection | MCP-readable source-return packet |
| receipt | validation receipt for the current owner route |

Every provider record checks freshness against
`stats/source_home.manifest.json`. Git holds compact provider records and
source-return handles. Runtime graph, vector, embedding, cache, and serving
state stay with runtime owners.
