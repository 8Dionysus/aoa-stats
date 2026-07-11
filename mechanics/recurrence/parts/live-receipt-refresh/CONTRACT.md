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
- for every admitted profile, a current owner source and an observation route
  capable of causing refresh when that source changes
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
- the current 25-profile managed universe yields exactly 13 admitted live
  outputs and 12 false-live cleanup targets
- resolving a current owner path on demand does not replace a refresh
  observation route
- cleanup covers the full managed active-profile output set, including
  reference-only outputs, so stale runtime copies do not survive
- live materialization does not invoke the Component Refresh, Continuity
  Window, Codex Plane Deployment, Memory Movement, Stress Recovery, trusted
  rollout-history, or cadence-example reference adapters or infer their
  missing owner-runtime, observation, deploy-local, or active-cadence state
- derived views cannot strengthen owner evidence or become owner truth

Component Refresh remains a committed reference surface. Live activation
requires an explicit owner-runtime artifact carrying the reviewed chain from
drift hint through decision to owner-local refresh receipt; the live receipt
registry does not currently provide that chain.

Continuity Window also remains a committed reference surface. Its current
inputs are an aoa-agents example, an experimental aoa-playbooks contract, an
aoa-memo example, and draft anchors in the aoa-evals catalog. Live activation
requires a real timestamped owner-runtime continuity artifact or receipt with
resolvable continuity, revision, reanchor or explicit no-drift, and anchor
references plus applicable proof reports. The live receipt registry does not
currently provide that chain.

Codex Plane Deployment remains a committed owner-example reference surface.
Live refresh passes the explicit federation/workspace root into the no-fallback
live adapter, which may read only the trust-state, regeneration-report, and
rollout-receipt artifacts below `.codex/generated/rollout/`. Until a real
producer and refresh trigger are proven, the authored selector stays false and
stale runtime copies are removed.

Owner Landing remains a committed receipt-example surface. The accepted event
kinds and deterministic builder do not prove that `aoa-skills`, Dionysus, or
another named owner currently publishes the landing receipts. Until a real
owner-local publisher and observation route exist, the authored selector stays
false and stale runtime copies are removed.

Memory Movement remains a committed snapshot of real reviewed `aoa-memo`
corpus truth. Its catalog, object corpus, reviewed intake, and landing receipts
are authentic owner sources, but none of those four roots currently causes the
live refresh loop to run. Watching the separate memo writeback receipt log does
not prove observation of corpus movement. Until that trigger is explicit and
tested, the authored selector stays false and stale runtime copies are removed.

Stress Recovery Window remains a committed draft-eval example surface. Its
event envelope and example report demonstrate projection shape, not an active
`aoa-evals` publisher or a current report family. Until real owner receipts,
reports, and their observation route exist, the authored selector stays false
and stale runtime copies are removed.

This contract does not certify that every other `live_state_capable: true`
profile is receipt-backed. Their declared source postures require separate,
profile-by-profile audits.

## Crosswalk

This part operates on stats source-family id `intake_contract`. The reciprocal
route is recorded in `stats/source_home.manifest.json` and
`mechanics/topology.json`.

The selector/output split and stale-cleanup precedent is recorded for Component
Refresh in
`docs/decisions/AOST-D-0003-component-refresh-fixtures-are-not-live-state.md`.
The source-plus-observation admission law and the Owner Landing, Memory
Movement, and Stress Recovery audit are recorded in
`docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md`.

## Compatibility route

`scripts/check_live_publishers.py`, `scripts/refresh_live_stats.py`, and
`scripts/install_live_refresh_units.py` remain stable root commands. They
delegate to the canonical implementations in this part's `scripts/` district;
they do not own duplicate operation logic.
