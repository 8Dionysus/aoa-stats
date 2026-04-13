# aoa-stats

Derived observability and machine-first summary layer for the AoA federation.

`aoa-stats` is the downstream adjunct that consumes source-owned receipts,
evidence refs, and bounded eval verdicts to build machine-readable summaries
without taking ownership away from `aoa-skills`, `aoa-evals`, `aoa-playbooks`,
`aoa-techniques`, `aoa-agents`, `aoa-memo`, or `abyss-stack`.

This repository exists so project growth can stay visible during real work and
real sessions while preserving the canonical split:

- owner repos say what happened and what it means
- `aoa-stats` derives how often, how broadly, and how movement looks across
  named windows and pipelines
- project-core kernel usage is read from its own summary surface rather than
  inferred from total receipt volume

> Current release: `v0.1.1`. See [CHANGELOG](CHANGELOG.md) for release notes.

## Start here

Use the shortest route by need:

- ownership and anti-collapse rule: `docs/BOUNDARIES.md`
- five-layer architecture and derived posture: `docs/ARCHITECTURE.md`
- repo-local Codex MCP surface: `docs/CODEX_MCP.md`
- live receipt intake and generation loop: `docs/LIVE_SESSION_USE.md`
- current direction and live summary contour: `ROADMAP.md`, `README.md#current-v0-surface`, and `docs/README.md`
- release and publication posture: `docs/RELEASING.md` and `CHANGELOG.md`
- local agent instructions: `AGENTS.md`

## Route by need

- current derived schemas: `schemas/`
- first-wave derived antifragility vector doctrine and contract:
  `docs/ANTIFRAGILITY_VECTOR.md`,
  `schemas/antifragility_vector_v1.json`, and
  `examples/antifragility_vector.example.json`
- fourth-wave derived stress recovery doctrine and contracts:
  `docs/STRESS_RECOVERY_WINDOW_SUMMARIES.md`,
  `docs/DERIVED_SIGNAL_HYGIENE.md`,
  `schemas/stress_recovery_window_summary_v1.json`, and
  `examples/stress_recovery_window_summary.example.json`
- fourth-wave next-kernel branch and automation follow-through summaries:
  `docs/SESSION_GROWTH_BRANCH_SUMMARY.md`,
  `schemas/session-growth-branch-summary.schema.json`,
  `examples/session_growth_branch_summary.example.json`,
  `generated/session_growth_branch_summary.min.json`,
  `docs/AUTOMATION_FOLLOWTHROUGH_SUMMARY.md`,
  `schemas/automation-followthrough-summary.schema.json`,
  `examples/automation_followthrough_summary.example.json`, and
  `generated/automation_followthrough_summary.min.json`
- Codex-plane deployment continuity summary:
  `docs/CODEX_PLANE_DEPLOYMENT_SUMMARIES.md`,
  `schemas/codex-plane-deployment-summary.schema.json`,
  `examples/codex_plane_deployment_summary.example.json`, and
  `generated/codex_plane_deployment_summary.min.json`
- trusted Codex rollout operations and drift summaries:
  `docs/CODEX_PLANE_DEPLOYMENT_SUMMARIES.md`,
  `schemas/codex-rollout-operations-summary.schema.json`,
  `schemas/codex-rollout-drift-summary.schema.json`,
  `examples/codex_rollout_operations_summary.example.json`,
  `examples/codex_rollout_drift_summary.example.json`,
  `generated/codex_rollout_operations_summary.min.json`, and
  `generated/codex_rollout_drift_summary.min.json`
- rollout campaign cadence companions:
  `docs/ROLLOUT_CAMPAIGN_SUMMARY.md`,
  `docs/DRIFT_REVIEW_SUMMARY.md`,
  `schemas/rollout-campaign-summary.schema.json`,
  `schemas/drift-review-summary.schema.json`,
  `examples/rollout_campaign_summary.example.json`,
  `examples/drift_review_summary.example.json`,
  `generated/rollout_campaign_summary.min.json`, and
  `generated/drift_review_summary.min.json`
- wave-nine self-agency continuity summary:
  `docs/CONTINUITY_WINDOW_SUMMARY.md`,
  `schemas/continuity-window-summary.schema.json`,
  `examples/continuity_window_summary.example.json`, and
  `generated/continuity_window_summary.min.json`
- wave-ten component refresh summary and stats-owned refresh law:
  `docs/COMPONENT_REFRESH_SUMMARIES.md`,
  `schemas/component-refresh-summary.schema.json`,
  `examples/summary_refresh_law.example.json`,
  `examples/component_refresh_summary.example.json`, and
  `generated/component_refresh_summary.min.json`
- growth-refinery funnel doctrine and contracts:
  `docs/GROWTH_FUNNEL_SUMMARY.md`,
  `schemas/candidate_lineage_summary.schema.json`,
  `examples/candidate_lineage_summary.example.json`, and
  `generated/candidate_lineage_summary.min.json`
- growth-refinery owner landing and pruning followthrough:
  `docs/OWNER_LANDING_SUMMARY.md`,
  `docs/SUPERSESSION_DROP_SUMMARY.md`,
  `schemas/owner-landing-summary.schema.json`,
  `schemas/supersession-drop-summary.schema.json`,
  `examples/owner_landing_summary.example.json`,
  `examples/supersession_drop_summary.example.json`,
  `generated/owner_landing_summary.min.json`, and
  `generated/supersession_drop_summary.min.json`
- via negativa pruning checklist:
  `docs/VIA_NEGATIVA_CHECKLIST.md`
- canonical shared receipt envelope and active event family:
  `schemas/stats-event-envelope.schema.json`
- example receipt feed: `examples/session_harvest_family.receipts.example.json`
- canonical live source registry for owner-local receipts:
  `config/live_receipt_sources.json`
- example live source registry for bounded docs/testing:
  `config/live_receipt_sources.example.json`
- repo-local Codex MCP entrypoint:
  `scripts/aoa_stats_mcp_server.py`,
  `src/aoa_stats_mcp/`,
  `tests/test_aoa_stats_mcp_state.py`, and
  `requirements-mcp.txt`
- generated summary surfaces: `generated/`
- builders and validators: `scripts/build_views.py`,
  `scripts/refresh_live_stats.py`,
  `scripts/check_live_publishers.py`,
  `scripts/install_live_refresh_units.py`, and
  `scripts/validate_repo.py`
- release and contribution guidance: `docs/RELEASING.md`,
  `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, and
  `CODE_OF_CONDUCT.md`
- local verification path: `python scripts/build_views.py --check`,
  `python scripts/validate_repo.py`, and `python -m pytest -q tests`

## What `aoa-stats` owns

This repository is the source of truth for:

- derived summary schemas for cross-repo stats read models
- the canonical shared receipt envelope and cross-repo event-kind vocabulary
  consumed by stats builders
- machine-first generated summary surfaces built from source-owned receipts
- deterministic builders and validators for derived views
- docs that define how counts, verdicts, progression, and evidence stay
  separated at the stats layer

## What it does not own

- It does not own workflow meaning from `aoa-skills`.
- It does not own proof meaning or verdict interpretation from `aoa-evals`.
- It does not own scenario composition from `aoa-playbooks`.
- It does not own role or checkpoint contracts from `aoa-agents`.
- It does not own memory or provenance-thread meaning from `aoa-memo`.
- It does not own runtime execution or closeout meaning from `abyss-stack`.
- It does not become a sovereign score empire or dashboard authority.

## Core rule

Source repos own meaning. `aoa-stats` owns derived views.

If a stats surface starts behaving like workflow authority, proof authority, or
quest-state authority, the layer is drifting out of bounds.

## Current v0 surface

The first usable derived summaries are:

- `generated/object_summary.min.json`
- `generated/core_skill_application_summary.min.json`
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
- `generated/runtime_closeout_summary.min.json`
- `generated/stress_recovery_window_summary.min.json`
- `generated/surface_detection_summary.min.json`
- `generated/summary_surface_catalog.min.json`

These are built from one bounded receipt feed and are intended to stay
machine-first, evidence-linked, and weaker than the owner-local source
surfaces they summarize.

`generated/candidate_lineage_summary.min.json` is the first v1
growth-refinery funnel slice. It reads only reviewed owner-local lineage
entries carried by receipts, keeps the stage route explicit, and excludes raw
checkpoint-note intake.

`generated/owner_landing_summary.min.json` and
`generated/supersession_drop_summary.min.json` are the bounded followthrough
companions for that funnel slice. They stay downstream of owner-local reviewed
landings and seed-owner traces, so `aoa-stats` can expose landing and pruning
legibility without becoming owner truth.

`generated/session_growth_branch_summary.min.json` and
`generated/automation_followthrough_summary.min.json` are the wave-four
companions for next-kernel branch hints and bounded automation follow-through.
They stay descriptive, reviewed-input only, and weaker than any owner-local
route, playbook, or approval surface.

`generated/codex_plane_deployment_summary.min.json` is the wave-six deployment
continuity companion. It stays downstream of `8Dionysus` trust-state and
rollout receipts plus the `aoa-sdk` typed deploy-status snapshot, so
`aoa-stats` can expose trust counts and drift posture without becoming rollout
authority.

`generated/codex_rollout_operations_summary.min.json` and
`generated/codex_rollout_drift_summary.min.json` are the wave-seven companions
for checked-in trusted rollout campaign history in `8Dionysus/generated/codex/rollout/`.
They stay descriptive, current-campaign bounded, and weaker than source-owned
rollout history.

`generated/rollout_campaign_summary.min.json` and
`generated/drift_review_summary.min.json` are the wave-eight cadence
companions for source-owned campaign windows in
`8Dionysus/examples/*.example.json`. They stay descriptive, review-window
bounded, and weaker than both checked-in rollout history and source-owned
cadence windows.

`generated/continuity_window_summary.min.json` is the wave-nine self-agency
continuity companion. It derives one bounded continuity snapshot from the
public `aoa-agents` continuity window example, the sovereign continuity
playbook, a memo-side provenance thread, and the landed continuity eval
anchors. It stays descriptive, static-snapshot scoped, and weaker than all of
those owner-owned surfaces.

`generated/component_refresh_summary.min.json` is the wave-ten component
refresh companion. It derives one bounded refresh snapshot from the reviewed
`aoa-sdk` drift-hint and followthrough-decision examples, keeps owner repo and
status windows explicit, and stays weaker than owner laws, owner receipts, and
any real refresh validation.

`generated/summary_surface_catalog.min.json` is also the compact runtime-entry
capsule that federation routing should inspect first for `aoa-stats`. It now
ships as the schema-backed v2 runtime capsule with explicit `schema_ref`,
`owner_repo`, `surface_kind`, `authority_ref`, top-level `validation_refs`,
and route-level `surface_ref` fields for low-context readers.

`surface_detection_summary.min.json` is second-wave descriptive only. It may
count shortlist ambiguity, candidate posture, and closeout-handoff volume when
owner receipts preserve that context, but it does not decide promotion or
owner meaning.

Raw logs stay append-only. When receipts carry `supersedes`, the committed and
live summaries read from the active receipt view after local correction
collapse, not from raw line volume.

For real local session work, keep the committed `generated/` surfaces stable
and refresh ephemeral live state under `state/`.

## Verify current repo state

```bash
python scripts/build_views.py --check
python scripts/validate_repo.py
python -m pytest -q tests
```

For the optional repo-local MCP slice:

```bash
python -m pytest -q tests/test_aoa_stats_mcp_state.py
python scripts/aoa_stats_mcp_server.py
```

## Local build

Refresh the derived surfaces from one or more receipt feeds:

```bash
python scripts/build_views.py \
  --input examples/session_harvest_family.receipts.example.json \
  --output-dir generated
```

Refresh the local live state from owner-local source feeds under `/srv`:

```bash
python scripts/refresh_live_stats.py
```

Audit all required live publishers before or after a refresh:

```bash
python scripts/check_live_publishers.py
```

Install the user-level watcher so live summaries refresh automatically whenever
an owner-local receipt log changes:

```bash
python scripts/install_live_refresh_units.py --enable
```

The canonical watcher currently listens to these owner-local logs:

- `/srv/aoa-skills/.aoa/live_receipts/session-harvest-family.jsonl`
- `/srv/aoa-skills/.aoa/live_receipts/core-skill-applications.jsonl`
- `/srv/aoa-evals/.aoa/live_receipts/eval-result-receipts.jsonl`
- `/srv/aoa-playbooks/.aoa/live_receipts/playbook-receipts.jsonl`
- `/srv/aoa-techniques/.aoa/live_receipts/technique-receipts.jsonl`
- `/srv/aoa-memo/.aoa/live_receipts/memo-writeback-receipts.jsonl`
- `/srv/abyss-stack/.aoa/live_receipts/runtime-wave-closeouts.jsonl`

## Go elsewhere when...

- you need the workflow that emitted the receipt: `aoa-skills`
- you need proof meaning or eval verdict interpretation: `aoa-evals`
- you need reusable practice meaning: `aoa-techniques`
- you need scenario composition: `aoa-playbooks`
- you need role or checkpoint meaning: `aoa-agents`
- you need memory or provenance ownership: `aoa-memo`
- you need runtime-local trial or closeout truth: `abyss-stack`

## License

Apache-2.0
