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
│   ├── README.md
│   ├── operation-contract.schema.json
│   └── active/
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
| `operation-contracts` | One authored question, input posture, authority ceiling, consumer risk, and owner-return route per active non-catalog observation. | Exact reciprocal records for Agon registries, Experience contracts, via-negativa, and Titan memory/runtime parts. |
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
- non-catalog part-local operations cross back through one authored record in
  `stats/operation-contracts/active/`
- owner-local live-source registration belongs to the recurrence mechanic
- committed derived surfaces remain under `generated/`
- builders and readers remain under `src/`
- the Component Refresh reference profile uses the filesystem-free projection
  at `src/aoa_stats_builder/component_refresh.py` and the committed
  reviewed-example adapter at
  `src/aoa_stats_builder/component_refresh_sources.py`; it is not admitted to
  local live state
- the Continuity Window reference profile uses the filesystem-free projection
  at `src/aoa_stats_builder/continuity_window.py` and the explicit
  example/catalog adapter at `src/aoa_stats_builder/continuity_window_sources.py`;
  its represented posture is committed reference state, not current runtime
  continuity
- the Codex Plane Deployment reference profile uses the filesystem-free
  projection at `src/aoa_stats_builder/codex_plane_deployment.py` and the
  owner-example adapter at
  `src/aoa_stats_builder/codex_plane_deployment_sources.py`; its committed
  8Dionysus example chain is not deploy-local rollout state
- the Growth Cycle profile family shares deterministic projection through
  `src/aoa_stats_builder/growth_cycle.py`, with its focused package check under
  `mechanics/growth-cycle/tests/`
- public and compatibility commands remain under `scripts/`
- repo-wide and compatibility validation remains under root `scripts/` and
  `tests/`; operation-focused validation follows `mechanics/topology.json`,
  normally at the nearest part and at package level only for declared shared
  core
- the current MCP remains a read-only derived access route to the root
  boundaries, part-local live-source registry, catalog, and catalog-listed
  surfaces

`live_state_capable` in each active read-model profile is the executable live
materialization selector. The committed catalog may include reference-only
profiles; the local live catalog contains only admitted, materialized outputs,
while cleanup still covers every managed active output. Component Refresh,
Continuity Window, Codex Plane Deployment, trusted rollout-history, and both
cadence projections are currently reference-only alongside the Titan
references. The
selector and stale-cleanup precedent is recorded for Component Refresh in
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`;
that record is not a decision for the other reference-only profiles, and
the selector does not independently certify any profile's source posture.

Follow the family route card before changing any of those paths.
