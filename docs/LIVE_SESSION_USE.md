# Live Session Use

## Purpose

This guide defines the smallest honest loop for keeping the project's derived
stats current while real sessions are happening.

## Core loop

1. keep source-owned receipts near their owner surfaces
2. refresh one bounded local feed into `state/live_receipts.min.json`
3. rebuild local derived views under `state/generated/`
4. inspect the machine-first summaries without treating them as proof authority

## Default live command

```bash
python scripts/refresh_live_stats.py
```

By default this reads the registry at
`config/live_receipt_sources.json`, resolves sibling owner-local
sources under the current federation root, writes one combined local feed to
`state/live_receipts.min.json`, and rebuilds:

- `state/generated/object_summary.min.json`
- `state/generated/core_skill_application_summary.min.json`
- `state/generated/repeated_window_summary.min.json`
- `state/generated/route_progression_summary.min.json`
- `state/generated/fork_calibration_summary.min.json`
- `state/generated/automation_pipeline_summary.min.json`
- `state/generated/runtime_closeout_summary.min.json`
- `state/generated/summary_surface_catalog.min.json`

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

## Canonical repo surfaces

The committed builder refreshes:

- `generated/object_summary.min.json`
- `generated/core_skill_application_summary.min.json`
- `generated/repeated_window_summary.min.json`
- `generated/route_progression_summary.min.json`
- `generated/fork_calibration_summary.min.json`
- `generated/automation_pipeline_summary.min.json`
- `generated/runtime_closeout_summary.min.json`
- `generated/summary_surface_catalog.min.json`

## Live local surfaces

The live refresh path writes the same shape under `state/generated/` so the
repo can keep deterministic committed outputs while the local operator keeps a
current working read.

## Automatic watcher

Install the user-level watcher once:

```bash
python scripts/install_live_refresh_units.py --enable
```

This installs `aoa-stats-live-refresh.path` and
`aoa-stats-live-refresh.service` into `~/.config/systemd/user/`, ensures the
canonical owner-local live receipt logs exist, and refreshes `aoa-stats` every
time any watched JSONL file changes:

- `/srv/aoa-skills/.aoa/live_receipts/session-harvest-family.jsonl`
- `/srv/aoa-skills/.aoa/live_receipts/core-skill-applications.jsonl`
- `/srv/aoa-evals/.aoa/live_receipts/eval-result-receipts.jsonl`
- `/srv/aoa-playbooks/.aoa/live_receipts/playbook-receipts.jsonl`
- `/srv/aoa-techniques/.aoa/live_receipts/technique-receipts.jsonl`
- `/srv/aoa-memo/.aoa/live_receipts/memo-writeback-receipts.jsonl`
- `/srv/abyss-stack/.aoa/live_receipts/runtime-wave-closeouts.jsonl`

## Boundary reminder

If a live stats read and an owner-local source disagree, trust the owner-local
source and repair the derivation.
