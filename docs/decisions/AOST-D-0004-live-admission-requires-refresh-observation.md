# AOST-D-0004 Live Admission Requires Refresh Observation

## Index Metadata

- Decision ID: AOST-D-0004
- Original date: 2026-07-11
- Surface classes: stats/read-models, mechanics/recurrence, mechanics/method-growth, mechanics/boundary-bridge, mechanics/antifragility, src/adapters, state/generated, MCP/catalog
- Stats surfaces: live summary catalog, Owner Landing, Memory Movement, Stress Recovery Window
- Source lanes: owner-local landing receipts, aoa-memo reviewed corpus, aoa-evals stress-recovery receipts and reports
- Guard families: derived-only authority, live-source admission, refresh observation, profile-output parity, stale-output cleanup
- Posture: accepted

## Status

Accepted

## Context

`live_state_capable` controls which authored profiles the local refresh loop may
materialize and advertise under `state/generated/`. The Component Refresh
decision established that reviewed examples are not live state, but deliberately
left the remaining `true` profiles for separate source audits.

That audit exposed three different gaps.

- Owner Landing has committed `reviewed_owner_landing_receipt` and
  `seed_owner_landing_trace_receipt` examples, but no real owner publisher or
  matching receipt in the active owner feeds.
- Stress Recovery has a draft eval contract and an example report. Its
  committed receipt still uses an older report ref that the builder maps to the
  relocated example; no current stress-recovery receipt/report producer exists.
- Memory Movement reads authentic reviewed `aoa-memo` corpus truth rather than
  fixtures. However, the automatic refresh path watches the memo writeback
  receipt log and not the catalog, reviewed objects, reviewed-intake packets,
  or landing receipts from which this summary is derived. Corpus movement can
  therefore leave a previously advertised local summary stale.

A source being readable at manual build time is not enough to keep local state
continuously current.

## Decision

Live admission requires two independently explicit contracts:

1. a current owner source that the projection may read without strengthening
   its authority; and
2. an observation route that causes refresh when that source changes.

If either side is absent, the active profile stays available as a committed
reference surface but sets `live_state_capable: false`. The live refresh loop
omits it from the live catalog and removes stale managed runtime copies.

Owner Landing, Memory Movement, and Stress Recovery Window are therefore
reference-only in the current contract. The managed inventory remains 25
profiles, with 13 admitted to live materialization and 12 kept on committed or
reference routes.

Memory Movement retains its exact four-root `aoa-memo` source adapter and its
filesystem-free projection core because its source is real owner truth. Future
live activation needs a tested owner signal or watcher contract that observes
catalog, reviewed-object, reviewed-intake, and landing movement without
mutating or pretending to own those sources.

Owner Landing activation needs a real owner publisher and current receipts for
the named event kinds. Stress Recovery activation needs an activated owner eval
producer, a current report contract, and a refresh-observed receipt chain. Its
temporary report-ref relocation was a committed-reference compatibility
allowance, never a live fallback. Once authored consumers carry the canonical
owner ref, the exact adapter must not keep that relocation alive.

## Implementation Update - 2026-07-12

The `aoa-memo` recovery pattern and `aoa-routing` authored composite-stress
examples now cite the current mechanic-owned Stress Recovery eval path. The
`aoa-stats` intake fixture does the same, so the explicit retired bundle-path
translation has been removed from `stress_recovery_sources.py`.

This does not activate the surface. The eval remains a committed draft example,
and no refresh-observed owner receipt/report producer has landed. Stress
Recovery therefore remains active as a public reference contract with
`live_state_capable: false` under this decision.

## Options Considered

- Keep all three profiles live-admitted because their builders can return an
  output: confuses buildability with currentness and leaves stale or
  example-backed files advertised as live.
- Keep Memory Movement live because its corpus is authentic: preserves source
  classification, but ignores that the installed refresh mechanism cannot
  observe the source contract it advertises.
- Add recursive consumer-side filesystem watches immediately: closes part of
  the trigger gap, but couples stats to owner internals and does not prove
  reliable observation for nested object changes.
- Treat source and observation as one activation boundary: preserves useful
  committed summaries while making absence in local live state explicit until
  both halves are real.

## Rationale

`state/generated/` is operational state, not merely another place to copy a
committed snapshot. A consumer should be able to assume that an advertised live
surface is refreshed from its declared current source when that source moves.
Otherwise the live catalog converts an unobserved historical read into a
currentness claim.

The rule does not weaken `aoa-memo` corpus authority or require an owner change.
It constrains only what `aoa-stats` may advertise as live. Likewise, keeping the
Owner Landing and Stress Recovery contracts active preserves their public
shapes without inventing publishers or proof events.

## Consequences

- The committed summaries and public schemas remain available for all three
  surfaces.
- The committed catalog describes all 25 active profiles and marks these three
  as non-live.
- A live refresh admits 13 profiles, omits these three from its live catalog,
  and removes stale runtime copies if present.
- Memory Movement and Stress Recovery use explicit source adapters plus
  filesystem-free cores; the Stress Recovery adapter now resolves only the
  exact current owner ref, while root build functions remain compatibility
  facades.
- The memo writeback receipt log is not treated as proof that reviewed corpus
  movement is observed atomically.
- A future trigger or publisher must land with focused validation before any of
  the three profile selectors return to `true`.

## Source Surfaces

- `stats/read-models/active/owner_landing_summary.profile.json`
- `stats/read-models/active/memory_movement_summary.profile.json`
- `stats/read-models/active/stress_recovery_window_summary.profile.json`
- `stats/source_home.manifest.json`
- `src/aoa_stats_builder/memory_movement.py`
- `src/aoa_stats_builder/memory_movement_sources.py`
- `src/aoa_stats_builder/stress_recovery.py`
- `src/aoa_stats_builder/stress_recovery_sources.py`
- `scripts/build_views.py`
- `mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json`
- `mechanics/recurrence/parts/live-receipt-refresh/scripts/refresh_live_stats.py`
- `mechanics/recurrence/parts/live-receipt-refresh/scripts/install_live_refresh_units.py`
- `mechanics/method-growth/parts/owner-landing/`
- `mechanics/boundary-bridge/parts/memory-owner-handoff/`
- `mechanics/antifragility/parts/stress-recovery-windows/`

## Validation

Decision-lane checks are owned by [`AGENTS.md#verify`](AGENTS.md#verify).
Affected source-home and mechanic checks route through their owning
`AGENTS.md` or `VALIDATION.md`, then the root
[`AGENTS.md#verify`](../../AGENTS.md#verify) gate.
