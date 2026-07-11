# AOST-D-0003 Component Refresh Fixtures Are Not Live State

## Index Metadata

- Decision ID: AOST-D-0003
- Original date: 2026-07-11
- Surface classes: stats/read-models, mechanics/recurrence, src/adapters, state/generated, MCP/catalog
- Stats surfaces: component refresh summary, live summary catalog, local live output inventory
- Source lanes: aoa-sdk reviewed component refresh examples, owner-local component refresh receipts
- Guard families: derived-only authority, live-source admission, profile-output parity, stale-output cleanup
- Posture: accepted

## Status

Accepted

## Context

The committed Component Refresh summary is derived from two reviewed
`aoa-sdk` example packets. Those examples are useful reference evidence, but
the owner contract explicitly does not auto-emit them and does not treat a
chosen follow-through route as a completed owner refresh receipt.

The local live refresh loop nevertheless rebuilt that example projection under
`state/generated/` because its output inventory was hardcoded independently of
the authored surface profiles. This made a historical reference snapshot look
like current live state and allowed stale runtime copies to survive when the
builder later omitted an optional surface.

This decision governs the Component Refresh surface and its reviewed-example
adapter. It does not certify the source posture of other profiles currently
marked `live_state_capable: true`; those require separate audits against their
own declared inputs.

## Decision

`live_state_capable` is the authored selector for local live materialization.
The live refresh operation emits and catalogs only surfaces whose active
profile sets that field to `true`, while its cleanup universe still includes
every managed active surface so stale runtime files are removed.

Component Refresh remains an active committed reference surface, but its
profile is not live-capable. A dedicated reference-source adapter may load the
reviewed `aoa-sdk` examples for the committed build and pass a validated input
bundle to a filesystem-free projection core. Live refresh supplies no such
bundle and must not fall back to examples, owner laws, or inferred route state.

A future live adapter requires an explicit owner-runtime artifact with the
reviewed chain from drift hint through decision to owner-local refresh receipt.
Adding that artifact to the shared stats receipt ABI is a separate owner and
contract decision.

## Options Considered

- Continue replaying the reviewed examples in live state: preserves current
  output count, but mislabels fixture provenance as current runtime evidence.
- Remove the Component Refresh surface entirely: eliminates the ambiguity, but
  discards a useful bounded public reference contract and its historical
  snapshot.
- Infer current posture from owner manifests and refresh laws: creates data
  without an observation or receipt and would make stats stronger than its
  owners.
- Keep the committed reference surface and make live admission explicit: keeps
  the useful contract while preserving absence until a real owner-runtime
  source exists.

## Rationale

`aoa-stats` owns projection and catalog shape, not the occurrence or success of
an owner refresh. A reviewed example proves that a packet shape can be
validated; it does not prove that the packet was emitted for the current
workspace or that a selected route ran successfully.

Deriving the live inventory from authored profiles also removes a second
source-of-truth list. The same profile field can constrain Recurrence output,
live catalog visibility, stale cleanup, and future MCP consumption without
letting any of those adapters redefine source meaning.

## Consequences

- The committed `generated/component_refresh_summary.min.json` remains a
  reference snapshot with explicit example provenance.
- A subsequent live refresh removes
  `state/generated/component_refresh_summary.min.json` as stale and does not
  recreate it without a real owner-runtime adapter.
- The live catalog omits the Component Refresh surface; the committed catalog
  continues to expose it with `live_state_capable: false`.
- Root build compatibility remains, but filesystem discovery moves behind an
  explicit reference adapter while reference packet validation and projection
  stay in the filesystem-free core.
- Future owner receipt support cannot silently reuse the example adapter; it
  must land an explicit source contract, validation, and activation change.

## Source Surfaces

- `stats/read-models/active/component_refresh_summary.profile.json`
- `stats/read-models/surface-profile.schema.json`
- `stats/source_home.manifest.json`
- `src/aoa_stats_builder/component_refresh.py`
- `src/aoa_stats_builder/component_refresh_sources.py`
- `src/aoa_stats_builder/surface_catalog.py`
- `scripts/build_views.py`
- `mechanics/recurrence/parts/component-refresh/CONTRACT.md`
- `mechanics/recurrence/parts/live-receipt-refresh/scripts/refresh_live_stats.py`
- `mechanics/recurrence/parts/live-receipt-refresh/docs/LIVE_SESSION_USE.md`

## Validation

Run:

```bash
python scripts/generate_decision_indexes.py
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python scripts/build_views.py --check
python -m pytest -q mechanics/recurrence/parts/component-refresh/tests mechanics/recurrence/parts/live-receipt-refresh/tests tests/test_aoa_stats_mcp_state.py
```
