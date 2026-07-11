# Live receipt refresh contract

## Purpose

Produce a deterministic, derived-only local stats view from receipt sources
admitted by the `intake_contract` family.

## Inputs

- this part's `config/live_receipt_sources.json`
- readable owner-local receipt files resolved through that registry
- receipts accepted by the canonical stats event envelope
- active authored read-model profiles, whose `live_state_capable` field selects
  the live materialization allowlist
- explicit federation-root and output overrides when supplied by the operator

## Outputs

- publisher audit findings
- `state/live_receipts.min.json` for the active local receipt view
- profile-admitted summaries under `state/generated/`
- `state/generated/summary_surface_catalog.min.json`, containing only surfaces
  admitted and materialized by the current live run
- rendered watcher units when the installer is explicitly invoked

## Invariants

- source receipt files are not rewritten by refresh
- supersession is resolved for the derived active view without erasing the
  append-only source history
- unknown event kinds fail before a summary is built
- missing or invalid required publishers remain visible as errors
- a surface with `live_state_capable: false` is not materialized or cataloged
- cleanup covers the full managed active-profile output set, including
  reference-only outputs, so stale runtime copies do not survive
- live materialization does not invoke the Component Refresh committed-example
  adapter or infer its missing owner-law state
- derived views cannot strengthen owner evidence or become owner truth

Component Refresh remains a committed reference surface. Live activation
requires an explicit owner-runtime artifact carrying the reviewed chain from
drift hint through decision to owner-local refresh receipt; the live receipt
registry does not currently provide that chain.

This contract does not certify that every other `live_state_capable: true`
profile is receipt-backed. Their declared source postures require separate,
profile-by-profile audits.

## Crosswalk

This part operates on stats source-family id `intake_contract`. The reciprocal
route is recorded in `stats/source_home.manifest.json` and
`mechanics/topology.json`.

The profile/output split is recorded in
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`.

## Compatibility route

`scripts/check_live_publishers.py`, `scripts/refresh_live_stats.py`, and
`scripts/install_live_refresh_units.py` remain stable root commands. They
delegate to the canonical implementations in this part's `scripts/` district;
they do not own duplicate operation logic.
