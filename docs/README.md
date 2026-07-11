# Documentation map

This directory contains repository-wide architecture, boundary, release,
decision, compatibility, and historical surfaces. Operation-specific
documentation lives with its mechanic part.

## Start here

- durable repository shape: [`../DESIGN.md`](../DESIGN.md)
- authored stats source home: [`../stats/README.md`](../stats/README.md)
- active read-model profiles: [`../stats/read-models/README.md`](../stats/read-models/README.md)
- non-catalog operation contracts:
  [`../stats/operation-contracts/README.md`](../stats/operation-contracts/README.md)
- operation topology: [`../mechanics/README.md`](../mechanics/README.md)
- ownership boundary: [`BOUNDARIES.md`](BOUNDARIES.md)
- derived-view architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- current direction: [`../ROADMAP.md`](../ROADMAP.md) and
  [`../README.md#current-v0-surface`](../README.md#current-v0-surface)
- durable rationale: [`decisions/README.md`](decisions/README.md)
- release route: [`RELEASING.md`](RELEASING.md)

## Operation documentation

| Concern | Active owner document |
| --- | --- |
| receipt ABI | `../stats/intake-contract/RECEIPT_ABI.md` |
| live receipt refresh | `../mechanics/recurrence/parts/live-receipt-refresh/docs/LIVE_SESSION_USE.md` |
| component recurrence declarations | `../mechanics/recurrence/parts/component-manifests/docs/RECURRENCE_DERIVED_SUMMARIES.md` |
| component refresh | `../mechanics/recurrence/parts/component-refresh/docs/COMPONENT_REFRESH_SUMMARIES.md` |
| continuity window | `../mechanics/recurrence/parts/continuity-window/docs/CONTINUITY_WINDOW_SUMMARY.md` |
| growth funnel and candidate lineage | `../mechanics/method-growth/parts/candidate-lineage/docs/GROWTH_FUNNEL_SUMMARY.md` |
| supersession and pruning | `../mechanics/method-growth/parts/supersession-pruning/docs/SUPERSESSION_DROP_SUMMARY.md` |
| session-growth branch | `../mechanics/growth-cycle/parts/session-growth-branch/docs/SESSION_GROWTH_BRANCH_SUMMARY.md` |
| automation follow-through | `../mechanics/growth-cycle/parts/automation-followthrough/docs/AUTOMATION_FOLLOWTHROUGH_SUMMARY.md` |
| source coverage | `../mechanics/audit/parts/source-coverage/docs/SOURCE_COVERAGE_SUMMARY.md` |
| drift review | `../mechanics/audit/parts/drift-shadow-review/docs/DRIFT_REVIEW_SUMMARY.md` |
| stress recovery | `../mechanics/antifragility/parts/stress-recovery-windows/docs/STRESS_RECOVERY_WINDOW_SUMMARIES.md` |
| chaos-wave stress example | `mechanics/antifragility/parts/stress-recovery-windows/docs/STRESS_RECOVERY_SUMMARIES_CHAOS_WAVE1.md` |
| memory movement | `../mechanics/boundary-bridge/parts/memory-owner-handoff/docs/MEMORY_MOVEMENT_SUMMARY.md` |
| Codex Plane deployment | `../mechanics/release-support/parts/codex-deployment-rollout/docs/CODEX_PLANE_DEPLOYMENT_SUMMARIES.md` |
| trusted rollout history | `../mechanics/release-support/parts/trusted-rollout-history/docs/TRUSTED_ROLLOUT_HISTORY_SUMMARIES.md` |
| rollout campaign | `../mechanics/release-support/parts/rollout-campaign/docs/ROLLOUT_CAMPAIGN_SUMMARY.md` |

Experience and Agon have denser local maps; start at
`../mechanics/experience/PARTS.md` or `../mechanics/agon/PARTS.md`.

## Repository-wide contracts

- surface strength: [`SURFACE_STRENGTH_MODEL.md`](SURFACE_STRENGTH_MODEL.md)
- derived signal precedence: [`DERIVED_SIGNAL_HYGIENE.md`](DERIVED_SIGNAL_HYGIENE.md)
- read-only MCP access: [`../stats/surface-catalog/CODEX_MCP.md`](../stats/surface-catalog/CODEX_MCP.md)
- consumer regrounding: [`../stats/surface-catalog/CONSUMER_REGROUNDING.md`](../stats/surface-catalog/CONSUMER_REGROUNDING.md)

`GROWTH_FUNNEL_SUMMARY.md`, `COMPONENT_REFRESH_SUMMARIES.md`, and
`RECURRENCE_DERIVED_SUMMARIES.md` are thin compatibility routes. Their linked
mechanic documents are authoritative.

## History

`history/AGENTS_ROOT_REFERENCE.md` preserves the former long root guidance as
provenance. It is not an active instruction surface.
