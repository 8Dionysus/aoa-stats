# AGENTS.md

Route card for the `stats/` source home.

## Scope

`stats/` owns the source-authored meaning of stats families: what an intake
contract admits, what a derived surface describes, and where each family's
authority stops.

It does not own operation payloads, generated outputs, Python implementation,
or source-owner facts. Those remain in the active routes named by
`source_home.manifest.json`.

## Start here

1. `README.md`
2. `source_home.manifest.json`
3. the selected family's `AGENTS.md`
4. the selected family's `README.md`
5. every current root route named by that family
6. every mechanics route named by that family before changing an operation

## Source-home law

- Keep source meaning and authority ceilings here.
- Keep implementation under `src/`, committed derived outputs under
  `generated/`, canonical published schemas under `schemas/`, and public or
  compatibility commands under `scripts/` unless their owner route changes
  explicitly.
- Keep only declared source records here: intake admission records, the bounded
  intake fixture, authored active/deferred read-model profiles, retired-output
  cleanup tombstones, and authored non-catalog operation records. Do not add
  `__init__.py`, executable payloads, generated JSON, owner-local receipt feeds,
  or runtime state under `stats/`.
- One current payload has one active owner. A source-family route may point to
  it; it must not duplicate it.
- Treat `source_home.manifest.json` as the machine-readable crosswalk. The
  branch READMEs explain it but do not override it.
- Keep this source-home README and branch README files as route atlases. Exact
  profile state belongs in the profile, operation maturity in its operation
  record, and rationale in indexed decisions; do not hand-maintain mutable
  surface counts or named live/reference rosters in entrypoint prose.
- Treat each active profile's `live_state_capable` value as the source-owned
  live-materialization selector. Mechanics may clean stale runtime copies of a
  non-live surface, but they must not publish that surface into live state or a
  live catalog.
- Retired profiles are cleanup and provenance records only. They must not
  re-enter the public catalog, committed build fanout, or live materialization.
- Retired profiles reserve their former catalog slots. Active profiles may
  leave gaps but must not reuse those slots or renumber unrelated surfaces.
- Former mechanic routes on retired records are historical identifiers; only
  active and deferred profile handoffs must resolve to active mechanic parts.

## Branch routes

- `intake-contract/` owns the shared stats receipt-envelope and event-family
  admission meaning, below each source repo's payload authority.
- `read-models/` owns active and deferred surface profiles plus minimal retired
  output tombstones, and hands repeatable operation to named mechanic parts.
- `operation-contracts/` owns one bounded stats question, evidence posture,
  authority ceiling, consumer risk, and owner-return route for each active
  part-local observation contract that does not publish a public catalog
  surface.
- `surface-catalog/` owns the meaning and authority ceilings of the compact
  generated summary-surface catalog, below every owner-local fact it indexes.

## Cross-route law

Every family entry must name:

- its source-authored meaning and owner ceiling
- the current root source and public contract routes
- implementation and validation routes that actually exist
- generated or read-only access routes when applicable
- the mechanics packages and parts that operate on the family

Changing source meaning requires checking both the current root contracts and
the paired mechanics routes. Changing an operation belongs in `mechanics/` and
must preserve the source-family ceiling declared here.

## Current root posture

The root `schemas/` and `generated/` districts remain active. The repo-local
MCP under `src/aoa_stats_mcp/` remains a read-only derived access surface over
the part-local live-source registry and generated catalog; it is not source
authority.

## Verify

```bash
python -m json.tool stats/source_home.manifest.json >/dev/null
python scripts/validate_stats_source_home.py
python scripts/build_views.py --check
python scripts/validate_nested_agents.py
python scripts/validate_repo.py
```

Run the focused validators and tests listed by the family you changed.
