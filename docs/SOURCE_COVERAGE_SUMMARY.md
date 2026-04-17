# Source Coverage Summary

## What this surface is

`generated/source_coverage_summary.min.json` is the stats layer watching its
own intake discipline.

It says which owner repos are actually represented in the active receipt feed,
which event families dominate the current picture, and which expected owners
are still missing.

## Why this exists

Without a coverage surface, `aoa-stats` can look fuller than it really is.

This summary keeps that honest by publishing:

- expected owner repos from the live source registry when present
- observed owner repos from active receipts
- missing and unexpected owner repos
- counts by owner repo and event kind
- thin-signal flags when the intake posture is narrow or skewed

## What it does not do

This surface does not:

- prove that an owner repo is healthy
- replace the live source registry
- replace owner-local receipt logs
- justify new summary families on its own

It is a derived intake audit, not a sovereignty claim.

## Input posture

The strongest path is:

1. canonical live source registry
2. owner-local append-only receipt feeds
3. active-receipt resolution after `supersedes`

If the registry is absent, the summary must say so through `source_mode` and
`thin_signal_flags`.

## Verification

Use:

```bash
python scripts/build_views.py --check
python scripts/refresh_live_stats.py
```

The committed generated file keeps the deterministic repo posture.
The live refresh path mirrors it under `state/generated/`.
