# Live Session Use

## Purpose

This guide defines the smallest honest loop for keeping the project's derived
stats current while real sessions are happening.

## Core loop

1. keep source-owned receipts near their owner surfaces
2. collect or mirror the receipts you want to summarize into one bounded feed
3. rebuild the derived views
4. inspect the machine-first summaries without treating them as proof authority

## Example command

```bash
python scripts/build_views.py \
  --input examples/session_harvest_family.receipts.example.json \
  --output-dir generated
```

## What to feed it

The current builder accepts one or more JSON files that contain an array of
receipt envelopes. Each receipt should include:

- `event_kind`
- `event_id`
- `observed_at`
- `run_ref`
- `session_ref`
- `actor_ref`
- `object_ref`
- `evidence_refs`
- `payload`

## Current output surfaces

The builder refreshes:

- `generated/object_summary.min.json`
- `generated/repeated_window_summary.min.json`
- `generated/route_progression_summary.min.json`
- `generated/fork_calibration_summary.min.json`
- `generated/automation_pipeline_summary.min.json`
- `generated/summary_surface_catalog.min.json`

## Boundary reminder

If a live stats read and an owner-local source disagree, trust the owner-local
source and repair the derivation.

