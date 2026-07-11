# aoa-stats roadmap

> Current release: `v0.1.3`

This is the current repo-owned direction surface. Shipped history belongs in
`CHANGELOG.md`; durable rationale belongs in `docs/decisions/`; the public
snapshot lives at `README.md#current-v0-surface`.

## Current release contour

The current line is derived-observability hardening: keep read models useful,
deterministic, and easy to consume while keeping them weaker than source-owned
receipts, proof, rollout history, runtime state, and owner decisions.

The source/mechanics refactor is part of that contour:

- `stats/intake-contract/` authors receipt admission meaning
- `stats/read-models/` authors each catalog profile
- `stats/operation-contracts/` authors one bounded source record per real
  non-catalog part contract
- `stats/surface-catalog/` authors catalog and read-only access posture
- `mechanics/` owns repeatable operations and their localized payload
- `schemas/` and `generated/` remain stable public publication districts
- `src/` remains the importable implementation and access boundary
- authored `live_state_capable` profiles select local live materialization;
  the current split is 16 live-admitted read models across 25 managed active
  outputs, and cleanup covers the full managed set

## Active summary families

The public v2 catalog currently exposes:

| Mechanic contour | Catalog families |
| --- | --- |
| Audit | core-skill application, object, source-coverage, surface-detection, drift-review |
| Method Growth | candidate-lineage, owner-landing, supersession-drop |
| Recurrence | repeated-window, continuity-window, component-refresh |
| RPG | route-progression |
| Growth Cycle | fork-calibration, session-growth branch, automation-pipeline, automation-followthrough |
| Release Support | Codex-plane deployment, rollout-operations, rollout-drift, rollout-campaign |
| Boundary Bridge | memory-movement |
| Checkpoint | runtime-closeout |
| Antifragility | stress-recovery |
| Titan | Titan-incarnation, Titan-summon |

The authoritative inventory is
`generated/summary_surface_catalog.min.json`, projected from the authored
profiles under `stats/read-models/active/`. The deferred Antifragility vector
contract stays separate from active catalog claims.

## Maintained contracts

- owner boundaries: `docs/BOUNDARIES.md`
- derived architecture: `docs/ARCHITECTURE.md`
- authored read-model map: `stats/read-models/README.md`
- non-catalog operation contracts: `stats/operation-contracts/README.md`
- public catalog contract: `schemas/summary-surface-catalog.schema.json`
- receipt ABI: `stats/intake-contract/RECEIPT_ABI.md`
- event-kind registry: `stats/intake-contract/event-kind-registry.json`
- live source registry:
  `mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json`
- live operation guide:
  `mechanics/recurrence/parts/live-receipt-refresh/docs/LIVE_SESSION_USE.md`
- surface strength: `docs/SURFACE_STRENGTH_MODEL.md`
- source coverage:
  `mechanics/audit/parts/source-coverage/docs/SOURCE_COVERAGE_SUMMARY.md`
- deployment observations:
  `mechanics/release-support/parts/codex-deployment-rollout/docs/CODEX_PLANE_DEPLOYMENT_SUMMARIES.md`
- trusted rollout-history observations:
  `mechanics/release-support/parts/trusted-rollout-history/docs/TRUSTED_ROLLOUT_HISTORY_SUMMARIES.md`
- committed Codex Plane Deployment reference boundary:
  `src/aoa_stats_builder/codex_plane_deployment.py` and
  `src/aoa_stats_builder/codex_plane_deployment_sources.py`; the current source
  is the bounded 8Dionysus owner-example chain, not deploy-local rollout state
- campaign and drift review:
  `mechanics/release-support/parts/rollout-campaign/docs/ROLLOUT_CAMPAIGN_SUMMARY.md`
  and `mechanics/audit/parts/drift-shadow-review/docs/DRIFT_REVIEW_SUMMARY.md`
- continuity and component refresh:
  `mechanics/recurrence/parts/continuity-window/docs/CONTINUITY_WINDOW_SUMMARY.md`
  and `mechanics/recurrence/parts/component-refresh/docs/COMPONENT_REFRESH_SUMMARIES.md`
- committed reference projection boundaries:
  `src/aoa_stats_builder/codex_plane_deployment.py`,
  `src/aoa_stats_builder/codex_plane_deployment_sources.py`,
  `src/aoa_stats_builder/codex_trusted_rollout.py`,
  `src/aoa_stats_builder/codex_trusted_rollout_sources.py`,
  `src/aoa_stats_builder/rollout_cadence.py`,
  `src/aoa_stats_builder/rollout_cadence_sources.py`,
  `src/aoa_stats_builder/continuity_window.py`,
  `src/aoa_stats_builder/continuity_window_sources.py`,
  `src/aoa_stats_builder/component_refresh.py`, and
  `src/aoa_stats_builder/component_refresh_sources.py`; the selector and
  stale-cleanup precedent comes from the Component Refresh-only decision
  `docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`
- live output lifecycle debt: add an explicit retired/renamed-output cleanup
  record before an active read-model profile leaves the managed inventory
- stress-recovery chaos fixture:
  `mechanics/antifragility/parts/stress-recovery-windows/examples/stress_recovery_window_summary.chaos-wave1.example.json`
- reviewed memory movement:
  `mechanics/boundary-bridge/parts/memory-owner-handoff/docs/MEMORY_MOVEMENT_SUMMARY.md`
- Growth Cycle projection contracts and shared core:
  `mechanics/growth-cycle/` and `src/aoa_stats_builder/growth_cycle.py`
- public catalog access: `stats/surface-catalog/CODEX_MCP.md`

## Direction

Changes on this line should:

1. start from owner evidence and either an authored stats profile or the
   explicit non-catalog operation-contract family
2. keep operation payload with the nearest mechanic part
3. preserve stable public schema and generated paths when consumers depend on
   them
4. expose missing or stale evidence instead of manufacturing certainty
5. update topology, source-home validation, focused tests, and generated
   outputs together
6. keep `README.md` and `docs/README.md` short and link-driven
7. keep all nine committed/reference profiles out of local live output until
   their real owner-runtime, deploy-local, or active-cadence sources and
   activation contracts exist; audit the remaining non-receipt or
   example-backed `live_state_capable: true` profiles separately

## Non-goals

The roadmap is not to widen into a dashboard empire, global score, hidden
scheduler, proof engine, route controller, memory owner, or runtime authority.
No summary may outrank the owner sources named by its profile. In particular,
rollout summaries remain weaker than source-owned rollout history and rollback
decisions.

## Release gate

```bash
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python scripts/validate_repo.py
python -m pytest -q tests mechanics
python scripts/release_check.py
```
