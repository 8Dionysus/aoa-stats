# Live Session Use

## Purpose

This guide defines the smallest honest loop for keeping the project's derived
stats current while real sessions are happening.

## Core loop

1. keep source-owned receipts near their owner surfaces
2. refresh one bounded local feed into `state/live_receipts.min.json`
3. materialize profile-admitted local views under `state/generated/`
4. inspect the machine-first summaries without treating them as proof authority

## Default live command

```bash
python scripts/refresh_live_stats.py
```

By default this reads the registry at
`mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json`,
resolves sibling owner-local sources under the current federation root, writes
one combined local feed to `state/live_receipts.min.json`, derives its
allowlist from active profiles with `live_state_capable: true`, and
admits the following read-model output names. Each is materialized only when its
declared source contract resolves:

- `state/generated/core_skill_application_summary.min.json`
- `state/generated/object_summary.min.json`
- `state/generated/candidate_lineage_summary.min.json`
- `state/generated/owner_landing_summary.min.json`
- `state/generated/supersession_drop_summary.min.json`
- `state/generated/repeated_window_summary.min.json`
- `state/generated/route_progression_summary.min.json`
- `state/generated/fork_calibration_summary.min.json`
- `state/generated/session_growth_branch_summary.min.json`
- `state/generated/automation_pipeline_summary.min.json`
- `state/generated/automation_followthrough_summary.min.json`
- `state/generated/codex_plane_deployment_summary.min.json`
- `state/generated/codex_rollout_operations_summary.min.json`
- `state/generated/codex_rollout_drift_summary.min.json`
- `state/generated/rollout_campaign_summary.min.json`
- `state/generated/drift_review_summary.min.json`
- `state/generated/continuity_window_summary.min.json`
- `state/generated/memory_movement_summary.min.json`
- `state/generated/runtime_closeout_summary.min.json`
- `state/generated/stress_recovery_window_summary.min.json`
- `state/generated/source_coverage_summary.min.json`
- `state/generated/surface_detection_summary.min.json`

It also writes the live-only catalog:

- `state/generated/summary_surface_catalog.min.json`

That catalog contains only outputs admitted and materialized by the current
live run. It does not copy the full committed catalog.

## What the builder accepts

The current builder accepts one or more JSON files that contain either:

- one receipt envelope object
- one array of receipt envelopes
- one JSONL file with one receipt envelope object per line

Each receipt should include:

- `event_kind`
- `event_id`
- `observed_at`
- `run_ref`
- `session_ref`
- `actor_ref`
- `object_ref`
- `evidence_refs`
- `payload`

Optional correction field:

- `supersedes`

`event_kind` must belong to the canonical shared event family in
`schemas/stats-event-envelope.schema.json`.
Unknown or misspelled kinds fail validation before any summary is built.
The active registry at `stats/intake-contract/event-kind-registry.json` must stay in
lockstep with that schema enum.

## Canonical repo surfaces

The committed builder publishes all 25 active reference and live-capable
profiles plus the public catalog:

- `generated/core_skill_application_summary.min.json`
- `generated/object_summary.min.json`
- `generated/candidate_lineage_summary.min.json`
- `generated/owner_landing_summary.min.json`
- `generated/supersession_drop_summary.min.json`
- `generated/repeated_window_summary.min.json`
- `generated/route_progression_summary.min.json`
- `generated/fork_calibration_summary.min.json`
- `generated/session_growth_branch_summary.min.json`
- `generated/automation_pipeline_summary.min.json`
- `generated/automation_followthrough_summary.min.json`
- `generated/codex_plane_deployment_summary.min.json`
- `generated/codex_rollout_operations_summary.min.json`
- `generated/codex_rollout_drift_summary.min.json`
- `generated/rollout_campaign_summary.min.json`
- `generated/drift_review_summary.min.json`
- `generated/continuity_window_summary.min.json`
- `generated/component_refresh_summary.min.json`
- `generated/memory_movement_summary.min.json`
- `generated/titan_incarnation_summary.min.json`
- `generated/titan_summon_summary.min.json`
- `generated/runtime_closeout_summary.min.json`
- `generated/stress_recovery_window_summary.min.json`
- `generated/source_coverage_summary.min.json`
- `generated/surface_detection_summary.min.json`
- `generated/summary_surface_catalog.min.json`

## Live local surfaces

The live refresh path does not mirror the committed output set. The active
profiles are the single inventory source:

- `live_state_capable: true` selects the materialization allowlist
- all active profile output names form the stale-file cleanup universe
- the live catalog lists only outputs actually materialized

The current false-live profiles are:

- `component_refresh_summary`
- `titan_incarnation_summary`
- `titan_summon_summary`

They remain valid committed public reference surfaces, but the live run does
not recreate them. If an older copy exists under `state/generated/`, cleanup
removes it. In particular, the Component Refresh adapter may load reviewed
`aoa-sdk` examples for the committed build only; it is never a live fallback.

Future Component Refresh live activation requires a canonical owner-runtime
artifact whose reviewed chain reaches an owner-local
`component_refresh_receipt`. Owner laws or example packets cannot fill that
absence. See
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`.

The live feed and committed builders keep raw logs append-only, but the
receipt-backed live summaries read from the active receipt view after local
`supersedes` resolution. Other true-live profiles may read their explicitly
declared current source contract; profile admission does not strengthen those
sources.

`source_coverage_summary` is the intake self-audit inside that loop. It keeps
missing owner repos, unexpected repos, and dominant intake skew visible so the
stats layer cannot quietly overstate its own reach.

Second-wave surface detection stays descriptive here as well. If owner-local
core-skill receipts preserve `surface_detection_context`, the builder may
derive shortlist ambiguity and closeout-handoff counts, but those counts do
not become routing or promotion authority.

## Automatic watcher

Install the user-level watcher once:

```bash
python scripts/install_live_refresh_units.py --enable
```

This installs `aoa-stats-live-refresh.path` and
`aoa-stats-live-refresh.service` into `~/.config/systemd/user/`, ensures the
canonical owner-local live receipt logs exist, and refreshes `aoa-stats` every
time any watched JSONL file changes:

The checked-in templates under
`mechanics/recurrence/parts/live-receipt-refresh/systemd/` are rendered by the
installer with concrete repo, registry, feed, summary, federation-root, and
watch paths before it writes user units.

- `/srv/AbyssOS/aoa-skills/.aoa/live_receipts/session-harvest-family.jsonl`
- `/srv/AbyssOS/aoa-skills/.aoa/live_receipts/core-skill-applications.jsonl`
- `/srv/AbyssOS/aoa-evals/.aoa/live_receipts/eval-result-receipts.jsonl`
- `/srv/AbyssOS/aoa-playbooks/.aoa/live_receipts/playbook-receipts.jsonl`
- `/srv/AbyssOS/aoa-techniques/.aoa/live_receipts/technique-receipts.jsonl`
- `/srv/AbyssOS/aoa-memo/.aoa/live_receipts/memo-writeback-receipts.jsonl`
- `/srv/AbyssOS/abyss-stack/.aoa/live_receipts/runtime-wave-closeouts.jsonl`

## Readiness audit

Audit all required live publishers before or after a refresh:

```bash
python scripts/check_live_publishers.py
```

This command checks that required sources named in
`mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json`
exist, are readable, and parse as receipts compatible with the canonical
shared envelope and event family.

## Boundary reminder

If a live stats read and an owner-local source disagree, trust the owner-local
source and repair the derivation.
