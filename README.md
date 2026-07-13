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

The checked source home carries receipt admission, authored read-model and
operation contracts, deterministic projection, stable public schemas, and
read-only catalog access. Exact lifecycle state comes from the profiles under
[`stats/read-models/`](stats/read-models/); non-catalog maturity comes from
[`stats/operation-contracts/`](stats/operation-contracts/); the compact public
projection is
[`generated/summary_surface_catalog.min.json`](generated/summary_surface_catalog.min.json).

### Public-root contracts

The root is intentionally narrow:

- `schemas/` — stable catalog and receipt contracts
- `generated/` — committed public read models
- `scripts/` — public, compatibility, and repo-wide commands
- `tests/` — repository and public-contract checks
- `docs/` — repository-wide architecture, boundaries, decisions, release
  guidance, and history
- `examples/codex_plane_deployment_summary.example.json` — retained external
  compatibility fixture
- `manifests/artifact_bundles/` — public summary-catalog bundle

Operation-owned config, docs, examples, supporting schemas, manifests,
systemd templates, builders, validators, and focused tests live under their
mechanic parts. `scripts/validate_mechanics_topology.py` enforces this
placement contract. A focused test shared by several parts may live at the
mechanic-package level only when it constrains one shared importable core and
that package payload root is declared in `mechanics/topology.json`.

The operation route starts at [`mechanics/README.md`](mechanics/README.md); its
machine-readable inventory and source-family crosswalk live in
[`mechanics/topology.json`](mechanics/topology.json). The root README does not
replay that changing part inventory.

## Build, live use, and verification

Use the working gate in [`AGENTS.md#verify`](AGENTS.md#verify), then follow the
nearest changed family's `AGENTS.md` and mechanic part's `VALIDATION.md`.
Script-specific working guidance stays in
[`scripts/AGENTS.md`](scripts/AGENTS.md).

For registered owner-local feeds and watcher use, follow the
[`live-receipt-refresh` operator guide](mechanics/recurrence/parts/live-receipt-refresh/docs/LIVE_SESSION_USE.md)
and its adjacent
[`VALIDATION.md`](mechanics/recurrence/parts/live-receipt-refresh/VALIDATION.md).

The active registry and watcher templates live in
`mechanics/recurrence/parts/live-receipt-refresh/`. Local refresh writes under
ignored `state/`; committed public output stays under `generated/`. Local live
materialization includes only active profiles with `live_state_capable: true`,
and its catalog lists only outputs actually materialized. Reference-only
profiles remain in the committed catalog and retired profiles remain explicit
stale-cleanup inputs. The authored profiles and indexed decisions own the exact
current admission and lifecycle rationale.

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
[`CHANGELOG.md`](CHANGELOG.md). Release commands stay in the release guide;
the normal repository gate stays in [`AGENTS.md#verify`](AGENTS.md#verify).
