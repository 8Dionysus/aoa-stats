# aoa-stats

`aoa-stats` is the derived observability organ of AoA. It turns bounded,
source-owned receipts and reviewed evidence into deterministic read models.
Those models help humans and tools see movement; they do not become workflow,
proof, route, memory, runtime, identity, or owner truth.

> Current release: `v0.1.3`

## Start here

1. [`AGENTS.md`](AGENTS.md) — operating law and verification route
2. [`DESIGN.md`](DESIGN.md) — durable source/mechanics architecture
3. [`stats/README.md`](stats/README.md) — authored stats source home
4. [`mechanics/README.md`](mechanics/README.md) — operation and payload map
5. [`docs/BOUNDARIES.md`](docs/BOUNDARIES.md) — authority stop-lines
6. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — derived-view layers
7. [`ROADMAP.md`](ROADMAP.md) and
   [`README.md#current-v0-surface`](README.md#current-v0-surface) — current contour
8. [`docs/decisions/`](docs/decisions/) — durable rationale, not status

## Authority map

| Concern | Authoritative surface | Weaker companions |
| --- | --- | --- |
| receipt admission | `stats/intake-contract/` and `schemas/stats-event-envelope.schema.json` | examples, live registry, generated summaries |
| read-model lifecycle and meaning | `stats/read-models/{active,deferred,retired}/*.profile.json` | public catalog, generated output, MCP projection |
| non-catalog stats contracts | `stats/operation-contracts/active/*.operation.json` | part-local payload and root compatibility routes |
| operation ownership | `mechanics/topology.json` and nearest part cards | root compatibility routes |
| implementation | `src/aoa_stats_builder/` and `src/aoa_stats_mcp/` | command entrypoints |
| public contracts | catalog schemas under `schemas/` | examples and docs |
| public derived output | `generated/*.min.json` | KAG indexes and consumer caches |
| local live output admission | `stats/read-models/active/*.profile.json#live_state_capable` | `state/generated/`, live catalog, watcher output |
| current operations | nearest mechanic part | compatibility docs and root launchers |

Generated, compact, KAG, MCP, and installed surfaces remain subordinate to
their authored source and named owner inputs.

## Current v0 surface

The checked source home contains:

- the canonical receipt intake contract and active event-kind registry
- 24 active authored read-model profiles, one deferred contract profile, and
  one retired-output cleanup tombstone
- 15 authored operation-contract records for active non-catalog parts
- deterministic projection core under `src/aoa_stats_builder/`, exposed by the
  repo-wide `scripts/build_views.py` entrypoint
- stable public schemas and committed summaries under `schemas/` and
  `generated/`
- read-only catalog access through `src/aoa_stats_mcp/`
- mechanics-local payload and validation for Agon, Antifragility, Audit,
  Boundary Bridge, Checkpoint, Experience, Growth Cycle, Method Growth,
  Recurrence, Release Support, RPG, and Titan

The exact catalog is
[`generated/summary_surface_catalog.min.json`](generated/summary_surface_catalog.min.json).
Its authored inputs live under [`stats/read-models/`](stats/read-models/).

### Public-root exceptions

The root is intentionally narrow:

- `schemas/` — stable catalog and receipt contracts
- `generated/` — committed public read models, including eight Agon registries
- `scripts/` — public, compatibility, and repo-wide commands
- `tests/` — repository and public-contract checks
- `docs/` — architecture, boundaries, decisions, release guidance, and three
  explicit compatibility routes
- `examples/codex_plane_deployment_summary.example.json` — retained external
  compatibility fixture
- `manifests/artifact_bundles/` — public summary-catalog bundle

Operation-owned config, docs, examples, supporting schemas, manifests,
systemd templates, builders, validators, and focused tests live under their
mechanic parts. `scripts/validate_mechanics_topology.py` enforces this
placement contract. A focused test shared by several parts may live at the
mechanic-package level only when it constrains one shared importable core and
that package payload root is declared in `mechanics/topology.json`.

## Important operation routes

- live intake and watchers:
  `mechanics/recurrence/parts/live-receipt-refresh/`
- component declarations and derived recurrence:
  `mechanics/recurrence/parts/component-manifests/`
- stress recovery:
  `mechanics/antifragility/parts/stress-recovery-windows/`, including
  `mechanics/antifragility/parts/stress-recovery-windows/docs/STRESS_RECOVERY_SUMMARIES_CHAOS_WAVE1.md`
  and
  `mechanics/antifragility/parts/stress-recovery-windows/examples/stress_recovery_window_summary.chaos-wave1.example.json`
- candidate lineage and growth funnel:
  `mechanics/method-growth/parts/candidate-lineage/`
- route-fork, session-branch, and automation follow-through projections:
  `mechanics/growth-cycle/`, backed by the shared deterministic core at
  `src/aoa_stats_builder/growth_cycle.py`
- committed Component Refresh reference projection:
  `mechanics/recurrence/parts/component-refresh/`, backed by
  `src/aoa_stats_builder/component_refresh.py` and the reviewed-example adapter
  at `src/aoa_stats_builder/component_refresh_sources.py`
- committed Continuity Window reference projection:
  `mechanics/recurrence/parts/continuity-window/`, backed by
  `src/aoa_stats_builder/continuity_window.py` and the explicit owner
  example/catalog adapter at `src/aoa_stats_builder/continuity_window_sources.py`
- memory movement and return to owner:
  `mechanics/boundary-bridge/parts/memory-owner-handoff/`, backed by the pure
  projection and explicit owner-corpus adapter at
  `src/aoa_stats_builder/memory_movement.py` and
  `src/aoa_stats_builder/memory_movement_sources.py`
- micro-friction contracts:
  `mechanics/experience/parts/micro-friction-receipts/`
- deployment and rollout observations:
  `mechanics/release-support/parts/codex-deployment-rollout/`
- Agon observability registries: `mechanics/agon/PARTS.md`

The full operation inventory is machine-readable in
[`mechanics/topology.json`](mechanics/topology.json).

## Build and verify

Install development dependencies, then run:

```bash
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python scripts/validate_repo.py
python -m pytest -q tests mechanics
```

To build from the checked receipt fixture:

```bash
python scripts/build_views.py \
  --input stats/intake-contract/examples/session_harvest_family.receipts.example.json \
  --output-dir /tmp/aoa-stats-generated
```

To inspect or refresh registered owner-local feeds:

```bash
python scripts/check_live_publishers.py
python scripts/refresh_live_stats.py
```

The active registry and watcher templates live in
`mechanics/recurrence/parts/live-receipt-refresh/`. Local refresh writes under
ignored `state/`; committed public output stays under `generated/`. Local live
materialization includes only active profiles with `live_state_capable: true`,
and its catalog lists only outputs actually materialized. Reference-only
profiles remain in the committed catalog and stale runtime copies are removed.
The managed inventory remains 25 read models; the authored live-admitted
allowlist contains 11. Checked-in trusted rollout history, the two committed
cadence-example projections, Owner Landing, Route Progression, Runtime
Closeout, Memory Movement, and Stress Recovery join Codex Plane Deployment,
Continuity Window, Component Refresh, and the two Titan surfaces on the
reference-only route.
[`AOST-D-0003`](docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md)
is the selector and stale-cleanup precedent established for Component Refresh,
while
[`AOST-D-0004`](docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md)
requires a current owner source and an observable refresh route for every live
profile. Continuity Window
is excluded because its current owner inputs are a committed example/catalog
chain rather than a real owner-runtime artifact or receipt. Codex Plane
Deployment is likewise excluded because its current output comes from three
committed 8Dionysus examples, not the deploy-local rollout artifact trio.
The rollout-history pair is excluded because checked-in review history is not
runtime state; the Campaign/Drift pair is excluded because its source is a
three-example cadence chain rather than an active producer.
Owner Landing and Stress Recovery lack real publishers; Memory Movement reads
real reviewed owner corpus truth, but that corpus has no refresh observation
route yet. Runtime Closeout remains bounded to the historical wave-receipt
fixture because the current `abyss-stack` trial receipt and the separate SDK
return receipt do not share its ABI; AOST-D-0006 forbids treating them as
implicit aliases.

For read-only MCP use, follow
[`stats/surface-catalog/CODEX_MCP.md`](stats/surface-catalog/CODEX_MCP.md).

## Boundaries

- Source repositories own payload meaning and current domain truth.
- `aoa-evals` owns bounded proof and verdict interpretation.
- `aoa-stats` owns only deterministic derivation and the shape of its read
  models.
- Missing, stale, rejected, or unregistered evidence stays visible; it is not
  converted into success or zero.
- A count, trend, or window cannot by itself prove mastery, intent, causality,
  self-agency, or owner health.

## Contribution and release

Use [`CONTRIBUTING.md`](CONTRIBUTING.md),
[`docs/RELEASING.md`](docs/RELEASING.md), and
[`CHANGELOG.md`](CHANGELOG.md). The complete release gate is:

```bash
python scripts/release_check.py
```
