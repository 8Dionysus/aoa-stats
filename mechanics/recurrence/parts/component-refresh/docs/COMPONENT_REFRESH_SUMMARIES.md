# Component Refresh Summaries

## Purpose

`generated/component_refresh_summary.min.json` is the derived-only stats view
for the wave-ten Component Refresh slice. Its committed content is a reference
snapshot.

It preserves one reviewed example of which named components appeared to drift,
which owner repos held the refresh route, and whether the represented posture
was active, deferred, or only recommended. It is not a current workspace
inventory.

## Boundary

This summary is weaker than:

- owner refresh laws in `8Dionysus`, `aoa-skills`, `aoa-agents`, and
  `aoa-stats`
- reviewed followthrough decisions in `aoa-sdk`
- real owner refresh receipts and validation in the owner repositories

The summary may describe refresh posture. It does not become refresh truth.
For this committed surface, that posture is only the one represented by its
reference inputs; it does not become current state.

## Inputs

The committed summary currently derives from reviewed `aoa-sdk` example
surfaces:

- `aoa-sdk/mechanics/checkpoint/parts/reviewed-closeout-context-carry/examples/component_drift_hints.example.json`
- `aoa-sdk/mechanics/checkpoint/parts/reviewed-closeout-context-carry/examples/component_refresh_followthrough_decision.example.json`

`src/aoa_stats_builder/component_refresh_sources.py` discovers and loads those
two authored fixtures for the committed build. It invokes the filesystem-free
reference validator, then passes an immutable input bundle to the projection in
`src/aoa_stats_builder/component_refresh.py`.

The examples keep the v1 public contract bounded and reviewable. Their
`reviewed` fields prove the example chain satisfies its reference contract;
they do not prove that equivalent packets were emitted for the current
workspace or that an owner refresh ran.

## Output shape

The summary keeps five things explicit:

- `owner_repo_counts`
- `status_counts`
- `drift_class_counts`
- one per-component row with the latest reviewed decision posture
- one bounded `generated_from` witness with source paths and freshness

When a component row is driven only by a reviewed decision and has no matching
per-component hint, `latest_observed_at` stays `null` rather than borrowing a
different component's freshness.

Reference status grammar:

- `current`
- `refresh_recommended`
- `refresh_active`
- `deferred`
- `recovered`

`refresh_recommended` is the bounded pre-execution posture. `refresh_active`
means a reviewed owner route has been chosen. `recovered` is reserved for a
later slice once owner receipts can prove recovery honestly.

## Live-state posture

The authored profile sets `live_state_capable: false`. Therefore
`python scripts/refresh_live_stats.py` does not materialize or advertise this
surface under `state/generated/`, and it does not silently fall back to the
reviewed examples. The live refresh cleanup universe still includes the
managed output name so an older runtime copy is removed as stale.

The committed catalog continues to expose the public reference profile. The
local live catalog contains only surfaces actually admitted and materialized
by their `live_state_capable: true` profiles.

Future live activation requires an explicit owner-runtime artifact with a
reviewed drift hint, followthrough decision, and stronger owner-local
`component_refresh_receipt`. Owner manifests and refresh laws may constrain
that chain but cannot substitute for an observation or receipt.

## Stats-owned refresh law

`../examples/summary_refresh_law.example.json` names the stats-side owner law
for `component:stats-derived-summaries:growth-refinery`.

That law keeps the refresh route narrow:

- reference source discovery stays in the reviewed-example adapter
- deterministic projection stays in the filesystem-free Component Refresh core
- the root builder remains a committed-build compatibility facade
- generated outputs stay in `generated/`
- owner validation remains stronger than any derived summary

The authority split and false-live admission rule are recorded in
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`.

## Negative rules

- Do not treat this summary as proof that a refresh succeeded.
- Do not treat a reviewed example or committed rebuild as current live state.
- Do not infer hidden automation or scheduler authority from this summary.
- Do not let stats overrule owner-local validation, receipts, or rollback
  anchors.
- Do not widen this surface into a cross-repo maintenance ledger.
