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
`config/live_receipt_sources.example.json`, resolves sibling owner-local
sources under the current federation root, writes one combined local feed to
`state/live_receipts.min.json`, and rebuilds:

- `state/generated/object_summary.min.json`
- `state/generated/repeated_window_summary.min.json`
- `state/generated/route_progression_summary.min.json`
- `state/generated/fork_calibration_summary.min.json`
- `state/generated/automation_pipeline_summary.min.json`
- `state/generated/summary_surface_catalog.min.json`

## What the builder accepts

The current builder accepts one or more JSON files that contain either:

- one receipt envelope object
- one array of receipt envelopes

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
- `generated/repeated_window_summary.min.json`
- `generated/route_progression_summary.min.json`
- `generated/fork_calibration_summary.min.json`
- `generated/automation_pipeline_summary.min.json`
- `generated/summary_surface_catalog.min.json`

## Live local surfaces

The live refresh path writes the same shape under `state/generated/` so the
repo can keep deterministic committed outputs while the local operator keeps a
current working read.

## Boundary reminder

If a live stats read and an owner-local source disagree, trust the owner-local
source and repair the derivation.
