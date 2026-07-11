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
│   ├── deferred/
│   └── retired/
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
| `read-models` | Active and deferred surface profiles plus minimal retired-output cleanup tombstones, including public routes, authority ceiling, order, lifecycle, and operation handoffs where applicable. | Profile-local mechanic routes under the shared mechanic parents. |
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
- the Audit core-skill application and surface-detection profiles share the
  finish-stage projection boundary at
  `src/aoa_stats_builder/core_skill_observation.py`, while Object Observation
  keeps its all-event projection separate at
  `src/aoa_stats_builder/object_observation.py`; focused validation follows the
  package and part owners declared in `mechanics/topology.json`
- the Route Progression profile names the RPG center and stronger receipt,
  agent-overlay, and SDK contract owners before handing its committed legacy
  numeric snapshot to `src/aoa_stats_builder/route_progression.py`; current
  semantic owner receipts are not scored, and focused proof belongs to
  `mechanics/rpg/parts/route-progression/tests/`
- the Runtime Closeout profile routes through the Checkpoint part and the
  filesystem-free historical compatibility projection at
  `src/aoa_stats_builder/runtime_closeout.py`; focused proof belongs to
  `mechanics/checkpoint/parts/runtime-closeout/tests/`, and current trial or
  return receipts are not silently treated as historical wave receipts
- the Repeated Window profile owns the observed-activity question while
  `src/aoa_stats_builder/repeated_window.py` conserves admitted receipt counts;
  focused invariant proof belongs to
  `mechanics/recurrence/parts/repeated-window/tests/`, and date buckets do not
  become claims of change or recurrence
- the active Titan Incarnation profile uses
  `src/aoa_stats_builder/titan_observation_sources.py` to load the exact
  committed example chain for validation by
  `src/aoa_stats_builder/titan_observation.py`; Titan Summon's former no-ledger
  baseline is retired, with only its public schema history and cleanup
  tombstone retained; focused proof belongs to
  `mechanics/titan/parts/incarnation-summon/tests/`
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
profiles; the local live catalog contains only admitted, materialized outputs.
Cleanup covers every active output plus every retired-output tombstone.
Component Refresh,
Continuity Window, Codex Plane Deployment, trusted rollout-history, and both
cadence projections are currently reference-only alongside Owner Landing,
Route Progression, Runtime Closeout, Memory Movement, Stress Recovery Window,
and Titan Incarnation. Owner
Landing and Stress Recovery still lack real publishers; Memory Movement has a
real reviewed owner corpus but no refresh observation route. The
selector and stale-cleanup precedent is recorded for Component Refresh in
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`;
the current-source plus observation requirement is recorded in
`docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md`.
The semantic-versus-numeric Route Progression boundary is recorded in
`docs/decisions/AOST-D-0005-route-progression-semantic-receipts-are-not-numeric-live-state.md`.
The historical-wave versus current-owner Runtime Closeout boundary is recorded
in
`docs/decisions/AOST-D-0006-runtime-closeout-wave-receipts-are-not-current-trial-live-state.md`.
The committed-roster versus observed-swarm Titan boundary is recorded in
`docs/decisions/AOST-D-0007-titan-reference-rosters-are-not-observed-swarm-activity.md`.
Titan Summon's removal from active stats and its cleanup-only lifecycle are
recorded in
`docs/decisions/AOST-D-0008-retired-outputs-remain-cleanup-tombstones-not-active-stats.md`.
The selector does not independently certify any profile's source posture.

Follow the family route card before changing any of those paths.
