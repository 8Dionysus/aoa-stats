# Component Refresh Summaries

## Purpose

`generated/component_refresh_summary.min.json` is the derived-only stats view
for the wave-ten component refresh slice.

It exists so the workspace can see which named components are drifting, which
owner repos currently hold the refresh route, and whether the current posture
is active, deferred, or only recommended.

## Boundary

This summary is weaker than:

- owner refresh laws in `8Dionysus`, `aoa-skills`, `aoa-agents`, and
  `aoa-stats`
- reviewed followthrough decisions in `aoa-sdk`
- real owner refresh receipts and validation in the owner repositories

The summary may describe refresh posture. It does not become refresh truth.

## Inputs

The committed summary currently derives from reviewed `aoa-sdk` example
surfaces:

- `aoa-sdk/examples/component_drift_hints.example.json`
- `aoa-sdk/examples/component_refresh_followthrough_decision.example.json`

That keeps the v1 surface bounded and reviewable while the owner-law family is
still being planted upstream.

## Output shape

The summary keeps five things explicit:

- `owner_repo_counts`
- `status_counts`
- `drift_class_counts`
- one per-component row with the latest reviewed decision posture
- one bounded `generated_from` witness with source paths and freshness

Current status grammar:

- `current`
- `refresh_recommended`
- `refresh_active`
- `deferred`
- `recovered`

`refresh_recommended` is the bounded pre-execution posture. `refresh_active`
means a reviewed owner route has been chosen. `recovered` is reserved for a
later slice once owner receipts can prove recovery honestly.

## Stats-owned refresh law

`examples/summary_refresh_law.example.json` names the stats-side owner law for
`component:stats-derived-summaries:growth-refinery`.

That law keeps the refresh route narrow:

- source inputs stay in `scripts/build_views.py`, `config/`, and repo docs
- generated outputs stay in `generated/`
- owner validation remains stronger than any derived summary

## Negative rules

- Do not treat this summary as proof that a refresh succeeded.
- Do not infer hidden automation or scheduler authority from this summary.
- Do not let stats overrule owner-local validation, receipts, or rollback
  anchors.
- Do not widen this surface into a cross-repo maintenance ledger.
