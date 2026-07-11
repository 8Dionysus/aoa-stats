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
  the current split is 11 live-admitted read models across 22 active outputs,
  while three retired-output tombstones keep cleanup at 25 managed names;
  Route Progression remains
  a committed legacy-numeric reference surface under AOST-D-0005 while the
  Runtime Closeout ABI distinction remains governed by AOST-D-0006 and its
  standalone historical snapshot is retired by AOST-D-0010;
  Titan Incarnation's committed-roster boundary is fixed by AOST-D-0007 and
  Titan Summon's cleanup-only retirement by AOST-D-0008; AOST-D-0009 retires
  the example-only Owner Landing aggregate and reserves former catalog slots

## Active summary families

The public v2 catalog currently exposes:

| Mechanic contour | Catalog families |
| --- | --- |
| Audit | core-skill application, object, source-coverage, surface-detection, drift-review |
| Method Growth | candidate-lineage, supersession-drop |
| Recurrence | repeated-window, continuity-window, component-refresh |
| RPG | route-progression |
| Growth Cycle | fork-calibration, session-growth branch, automation-pipeline, automation-followthrough |
| Release Support | Codex-plane deployment, rollout-operations, rollout-drift, rollout-campaign |
| Boundary Bridge | memory-movement |
| Antifragility | stress-recovery |
| Titan | Titan-incarnation |

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
  `src/aoa_stats_builder/component_refresh_sources.py`; Memory Movement and
  Stress Recovery use the same explicit core/source split through
  `src/aoa_stats_builder/memory_movement*.py` and
  `src/aoa_stats_builder/stress_recovery*.py`. The historical Runtime Closeout
  core is retired; only its schema, intake ABI, and cleanup tombstone remain.
  The selector and stale-cleanup
  precedent comes from the Component Refresh-only decision
  `docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`;
  the current-source plus refresh-observation admission rule is recorded in
  `docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md`
- live output lifecycle: `stats/read-models/retired/` now keeps explicit
  cleanup/provenance tombstones without retaining payloads or catalog entries;
  each tombstone reserves its former stable catalog slot
- stress-recovery chaos fixture:
  `mechanics/antifragility/parts/stress-recovery-windows/examples/stress_recovery_window_summary.chaos-wave1.example.json`
- reviewed memory movement:
  `mechanics/boundary-bridge/parts/memory-owner-handoff/docs/MEMORY_MOVEMENT_SUMMARY.md`
- Growth Cycle projection contracts and shared core:
  `mechanics/growth-cycle/` and `src/aoa_stats_builder/growth_cycle.py`
- Repeated Window source contract and Recurrence projection core:
  `stats/read-models/active/repeated_window_summary.profile.json`,
  `src/aoa_stats_builder/repeated_window.py`, and
  `mechanics/recurrence/parts/repeated-window/`
- Titan committed-reference and retirement boundaries:
  `stats/read-models/active/titan_incarnation_summary.profile.json`,
  `stats/read-models/retired/titan_summon_summary.profile.json`,
  `src/aoa_stats_builder/titan_observation.py`,
  `src/aoa_stats_builder/titan_observation_sources.py`, and
  `mechanics/titan/parts/incarnation-summon/`
- Owner Landing retirement and retained turnover-input boundary:
  `stats/read-models/retired/owner_landing_summary.profile.json`,
  `mechanics/method-growth/parts/supersession-pruning/`, and
  `docs/decisions/AOST-D-0009-retirement-reserves-catalog-slots-without-preserving-empty-mechanics.md`
- Runtime Closeout retirement and retained generic wave-receipt boundary:
  `stats/read-models/retired/runtime_closeout_summary.profile.json`,
  `stats/intake-contract/event-kind-registry.json`, and
  `docs/decisions/AOST-D-0010-runtime-closeout-wave-snapshot-is-contract-history-not-active-observability.md`
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
7. keep all 11 active committed/reference profiles out of local live output until
   their real owner-runtime, deploy-local, active-cadence, publisher, and
   refresh-observation contracts exist; audit every remaining
   `live_state_capable: true` profile against both its source and trigger

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
