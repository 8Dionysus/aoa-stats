# AGENTS.md

Guidance for coding agents and humans contributing to `aoa-stats`.

## Purpose

`aoa-stats` is the derived observability layer for AoA.
It consumes source-owned receipts, evidence refs, and bounded eval verdicts to
produce machine-readable summaries that help the project read movement during
work and sessions without stealing meaning from owner repositories.

This layer exists so growth can stay visible without turning dashboards into
sovereigns.

## Owns

This repository is the source of truth for:

- derived summary schemas
- the shared receipt envelope and event-kind vocabulary consumed by stats builders
- deterministic builders and validators for stats read models
- generated machine-first summary surfaces
- docs that define the stats-layer boundary and anti-collapse rules

## Does not own

Do not treat this repository as the source of truth for:

- workflow meaning in `aoa-skills`
- proof meaning or verdict interpretation in `aoa-evals`
- practice meaning in `aoa-techniques`
- scenario composition or questline posture in `aoa-playbooks`
- role, progression, or checkpoint meaning in `aoa-agents`
- memory or provenance-thread meaning in `aoa-memo`
- runtime execution or closeout meaning in `abyss-stack`
- live quest state, live route authority, or self-agent proof

## Core rules

Keep stats derived.

This layer may summarize counts, windows, and movement.
It must not replace bounded proof, workflow meaning, or route-state authority.

A stats surface may illuminate change.
It does not by itself prove mastery, intent, or self-agency.

## Read this first

Before making changes, read in this order:

1. `README.md`
2. `docs/BOUNDARIES.md`
3. `docs/ARCHITECTURE.md`
4. `docs/LIVE_SESSION_USE.md`
5. the schema, builder, or generated surface you plan to touch

Then branch by task:

- stress recovery or derived signal hygiene:
  `docs/STRESS_RECOVERY_WINDOW_SUMMARIES.md` and
  `docs/DERIVED_SIGNAL_HYGIENE.md`
- growth-refinery lineage funnel:
  `docs/GROWTH_FUNNEL_SUMMARY.md`,
  `schemas/candidate_lineage_summary.schema.json`, and
  `generated/candidate_lineage_summary.min.json`
- fourth-wave next-kernel branch and automation follow-through:
  `docs/SESSION_GROWTH_BRANCH_SUMMARY.md`,
  `docs/AUTOMATION_FOLLOWTHROUGH_SUMMARY.md`,
  `schemas/session-growth-branch-summary.schema.json`,
  `schemas/automation-followthrough-summary.schema.json`,
  `generated/session_growth_branch_summary.min.json`, and
  `generated/automation_followthrough_summary.min.json`
- growth-refinery owner landing and pruning followthrough:
  `docs/OWNER_LANDING_SUMMARY.md`,
  `docs/SUPERSESSION_DROP_SUMMARY.md`,
  `schemas/owner-landing-summary.schema.json`,
  `schemas/supersession-drop-summary.schema.json`,
  `generated/owner_landing_summary.min.json`, and
  `generated/supersession_drop_summary.min.json`
- component refresh summary and stats-owned refresh law:
  `docs/COMPONENT_REFRESH_SUMMARIES.md`,
  `schemas/component-refresh-summary.schema.json`,
  `examples/summary_refresh_law.example.json`,
  `examples/component_refresh_summary.example.json`, and
  `generated/component_refresh_summary.min.json`
- repo-local Codex MCP behavior:
  `docs/CODEX_MCP.md`,
  `scripts/aoa_stats_mcp_server.py`,
  `src/aoa_stats_mcp/`, and
  `tests/test_aoa_stats_mcp_state.py`
- receipt envelope or source-registry changes:
  `schemas/stats-event-envelope.schema.json`,
  `config/live_receipt_sources.json`, and
  `config/live_receipt_sources.example.json`
- live refresh or watcher behavior:
  `scripts/refresh_live_stats.py`,
  `scripts/check_live_publishers.py`, and
  `scripts/install_live_refresh_units.py`
- release prep or public repo hygiene:
  `docs/RELEASING.md`,
  `CHANGELOG.md`,
  `SECURITY.md`,
  `CONTRIBUTING.md`, and
  `CODE_OF_CONDUCT.md`

If a deeper directory defines its own `AGENTS.md`, follow the nearest one.

## Primary objects

The most important objects in this repository are:

- `docs/CODEX_MCP.md`
- `schemas/*.json`
- `schemas/stats-event-envelope.schema.json`
- `generated/session_growth_branch_summary.min.json`
- `generated/automation_followthrough_summary.min.json`
- `generated/*.json`
- `CHANGELOG.md`
- `docs/RELEASING.md`
- `config/live_receipt_sources*.json`
- `scripts/build_views.py`
- `scripts/check_live_publishers.py`
- `scripts/refresh_live_stats.py`
- `scripts/install_live_refresh_units.py`
- `scripts/aoa_stats_mcp_server.py`
- `scripts/validate_repo.py`
- `src/aoa_stats_mcp/`
- example receipt feeds under `examples/`
- tests that prove derivation and boundary integrity

## aoa-stats MCP posture

- Treat the `aoa_stats` MCP server as derived-only context.
- Start with `stats_catalog` before reading any specific surface.
- Prefer `stats_surface_read(..., mode="preview")` first; expand to `full`
  only when truly necessary.
- Use `stats_boundary_rules` whenever there is risk of treating counts or
  summaries as owner meaning.
- Never let `aoa-stats` override canonical meaning from `aoa-skills`,
  `aoa-evals`, `aoa-playbooks`, `aoa-techniques`, `aoa-agents`, `aoa-memo`,
  or `abyss-stack`.
- Do not extend this server toward raw receipt tailing, write actions, route
  authority, proof authority, or quest-state authority.

## Hard NO

Do not:

- let one summary surface pretend to be proof authority
- turn counts into a universal score
- duplicate raw artifacts when evidence refs are enough
- move workflow, proof, or role ownership into this repo
- let route progression or stress summaries become live quest authority
- infer self-agency or current truth from receipt volume alone
- quietly widen this repo into a dashboard monolith

## Contribution doctrine

Use this flow: `PLAN -> DIFF -> VERIFY -> REPORT`

### PLAN

State:

- which derived surface, schema, or builder is changing
- which owner repos supply the input facts
- whether output shape changes
- whether live receipt source registration changes
- what authority-drift risk exists

### DIFF

Keep the change focused.
Prefer deterministic derivation over hidden heuristics.
Do not mix unrelated cleanup into a stats change unless it is necessary for
repository integrity.

### VERIFY

Minimum validation:

```bash
python scripts/build_views.py --check
python scripts/validate_repo.py
python -m pytest -q tests
```

Use the live-loop verification path when the task touches refresh behavior,
watchers, or owner-local receipt intake:

```bash
python scripts/check_live_publishers.py
python scripts/refresh_live_stats.py
```

Confirm that:

- source ownership is still preserved
- generated outputs remain deterministic
- summaries stay machine-first, evidence-linked, and weaker than owner-local source surfaces
- progression, stress, route, or closeout summaries remain descriptive rather than authoritative
- no stats surface quietly becomes workflow, proof, or quest-state truth

### REPORT

Summarize:

- what changed
- which derived surfaces changed
- whether output shape changed
- which owner repos were involved
- what validation you actually ran
- any remaining boundary or rollout caveats

## Validation

Do not claim checks you did not run.
