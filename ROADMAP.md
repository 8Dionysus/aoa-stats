# AoA Stats Roadmap

This roadmap is the current repo-owned direction surface for `aoa-stats`.

Use it when the question is "what is the current derived-observability phase
and what should harden next?"
Use `README.md#current-v0-surface` and `docs/README.md` for the detailed map of
already-landed summary families.

## Current phase

`aoa-stats` has a real v0 derived surface.
The first usable summary families are already landed:

- object, core-skill application, candidate-lineage, owner-landing,
  supersession-drop, repeated-window, route-progression, and fork-calibration
  summaries
- session-growth branch, automation-pipeline, automation-followthrough, and
  runtime-closeout summaries
- Codex-plane deployment, rollout-operations, rollout-drift, rollout-campaign,
  drift-review, continuity-window, component-refresh, stress-recovery, and
  surface-detection summaries
- the summary-surface catalog plus the repo-local `aoa_stats` MCP read model

The next honest move is not to widen into a dashboard empire.
It is to keep derived summaries source-linked, hygienic, and explicit about
what they do not prove.

### Current release contour

The live `v0.1.1` contour is derived-observability hardening, not a new
workflow or proof layer. Its current checked surface is:

- boundary and architecture posture:
  `docs/BOUNDARIES.md`, `docs/ARCHITECTURE.md`,
  `docs/LIVE_SESSION_USE.md`, `docs/README.md`, and
  `schemas/stats-event-envelope.schema.json`
- compact runtime entry and catalog v2:
  `generated/summary_surface_catalog.min.json`,
  `schemas/summary-surface-catalog.schema.json`, and
  `tests/test_summary_surface_catalog.py`
- repo-local read-only Codex MCP:
  `docs/CODEX_MCP.md`, `scripts/aoa_stats_mcp_server.py`,
  `src/aoa_stats_mcp/server.py`, `src/aoa_stats_mcp/repo_state.py`,
  `tests/test_aoa_stats_mcp_state.py`, and `requirements-mcp.txt`
- rollout, cadence, drift, and continuity summary families:
  `docs/CODEX_PLANE_DEPLOYMENT_SUMMARIES.md`,
  `docs/ROLLOUT_CAMPAIGN_SUMMARY.md`, `docs/DRIFT_REVIEW_SUMMARY.md`,
  `docs/CONTINUITY_WINDOW_SUMMARY.md`,
  `generated/codex_rollout_operations_summary.min.json`,
  `generated/codex_rollout_drift_summary.min.json`,
  `generated/rollout_campaign_summary.min.json`,
  `generated/drift_review_summary.min.json`, and
  `generated/continuity_window_summary.min.json`
- deterministic builder and release validation:
  `scripts/build_views.py`, `scripts/validate_repo.py`, and
  `scripts/release_check.py`

This contour keeps Codex and rollout visibility derived, previewable, and
weaker than source-owned rollout history, continuity anchors, owner receipts,
and bounded eval verdicts.

## Current cycle

### Wave 1: root direction consolidation

Goals:

- keep `ROADMAP.md` as the root-level current-direction door
- keep `README.md` and `docs/README.md` short and link-driven
- route current shipped surfaces through `README.md#current-v0-surface` without
  duplicating phase snapshots everywhere

### Wave 2: summary contract hardening

Goals:

- keep schemas, builders, and generated summaries deterministic
- preserve shared receipt-envelope and live-source-registry discipline
- tighten route docs so derived surfaces do not masquerade as owner status

Exit signals:

- `python scripts/build_views.py --check` stays green
- `python scripts/validate_repo.py` stays green
- route docs, schemas, and generated summaries stay aligned under one bounded
  current-direction surface

### Wave 3: signal hygiene and live-intake discipline

Goals:

- preserve the distinction between counts, verdicts, progression, and evidence
  refs
- keep refresh and watcher tooling bounded to derived observability
- make new summary families earn their place through clear owner-linked inputs
  and explicit non-goals

### Wave 4: downstream readability without authority drift

Goals:

- keep the MCP and generated catalog fast for low-context inspection
- prefer compact preview surfaces over broader narrative duplication
- maintain the boundary against route, proof, checkpoint, or quest sovereignty

## Standing discipline

Across all waves:

- keep stats derived
- keep owner repos authoritative
- keep generated summaries compact and deterministic
- do not infer intent, mastery, or self-agency from counts alone
- do not let observability become workflow, proof, or route authority
