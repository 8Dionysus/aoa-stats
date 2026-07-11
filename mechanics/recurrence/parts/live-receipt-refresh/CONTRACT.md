# Live receipt refresh contract

## Purpose

Produce a deterministic, derived-only local stats view from receipt sources
admitted by the `intake_contract` family.

## Inputs

- this part's `config/live_receipt_sources.json`
- readable owner-local receipt files resolved through that registry
- receipts accepted by the canonical stats event envelope
- explicit federation-root and output overrides when supplied by the operator

## Outputs

- publisher audit findings
- `state/live_receipts.min.json` for the active local receipt view
- rebuilt summaries under `state/generated/`
- rendered watcher units when the installer is explicitly invoked

## Invariants

- source receipt files are not rewritten by refresh
- supersession is resolved for the derived active view without erasing the
  append-only source history
- unknown event kinds fail before a summary is built
- missing or invalid required publishers remain visible as errors
- derived views cannot strengthen owner evidence or become owner truth

## Crosswalk

This part operates on stats source-family id `intake_contract`. The reciprocal
route is recorded in `stats/source_home.manifest.json` and
`mechanics/topology.json`.

## Compatibility route

`scripts/check_live_publishers.py`, `scripts/refresh_live_stats.py`, and
`scripts/install_live_refresh_units.py` remain stable root commands. They
delegate to the canonical implementations in this part's `scripts/` district;
they do not own duplicate operation logic.
