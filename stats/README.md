# Stats source home

`stats/` is the source-authored home for the meaning and authority ceilings of
`aoa-stats` families. It tells a reader what the repository may derive and
routes that meaning to the root contracts, implementation, outputs,
validators, and mechanics that currently realize it.

It is not an importable Python package, generated-output directory, receipt
store, or second copy of root contracts.

## Shape

```text
stats/
├── AGENTS.md
├── README.md
├── source_home.manifest.json
├── intake-contract/
│   ├── AGENTS.md
│   ├── README.md
│   ├── RECEIPT_ABI.md
│   ├── event-kind-registry.json
│   └── examples/
├── read-models/
│   ├── AGENTS.md
│   ├── README.md
│   ├── surface-profile.schema.json
│   ├── active/
│   └── deferred/
├── operation-contracts/
│   ├── AGENTS.md
│   └── README.md
└── surface-catalog/
    ├── AGENTS.md
    ├── README.md
    ├── CODEX_MCP.md
    └── CONSUMER_REGROUNDING.md
```

## Families

| Family | Authored meaning | Mechanics crosswalk |
| --- | --- | --- |
| `intake-contract` | Shared stats envelope and event-family admission law, without taking payload meaning from source owners. | `recurrence/live-receipt-refresh`, `boundary-bridge/receipt-abi-crossing` |
| `read-models` | One authored profile per active or deferred derived surface, including public routes, authority ceiling, order, lifecycle, and operation handoffs. | Profile-local `mechanic_routes` under the shared mechanic parents. |
| `operation-contracts` | Stats meaning and authority ceilings for active part-local observations without public catalog surfaces. | Agon registries, Experience contracts, via-negativa, and Titan memory/runtime parts. |
| `surface-catalog` | Compact catalog profile and per-surface authority ceilings, without promoting summaries into owner truth. | `recurrence/component-manifests`, `boundary-bridge/consumer-regrounding` |

The full mechanics paths, current root routes, and validators are recorded in
`source_home.manifest.json`.

## Current canonical routes

The source home now owns its authored records while preserving public
publication and implementation districts:

- canonical receipt and catalog schemas remain under `schemas/`
- the active event-kind registry and bounded build fixture live under
  `stats/intake-contract/`
- read-model source profiles live under `stats/read-models/`
- non-catalog part-local operations cross back through
  `stats/operation-contracts/`
- owner-local live-source registration belongs to the recurrence mechanic
- committed derived surfaces remain under `generated/`
- builders and readers remain under `src/`
- public and compatibility commands remain under `scripts/`
- focused validation remains under `scripts/` and `tests/`
- the current MCP remains a read-only derived access route to the root
  boundaries, part-local live-source registry, catalog, and catalog-listed
  surfaces

Follow the family route card before changing any of those paths.
