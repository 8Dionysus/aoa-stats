# Receipt ABI crossing contract

## Purpose

Admit a bounded source-owned event family through one stable stats envelope
while preserving payload ownership and explicit consumer need.

## Inputs

- the canonical envelope at `schemas/stats-event-envelope.schema.json`
- the event-kind admission registry at
  `stats/intake-contract/event-kind-registry.json`
- payload-owner identity and at least one bounded stats summary family
- any declared downstream mirror of the envelope structure
- bounded JSON or JSONL receipt feeds, including explicit `supersedes` edges

## Outputs

- an active or deprecated event-kind admission record
- a validated shared envelope shape
- mirror-parity findings for declared downstream copies
- a deterministic latest-event feed and conservative active receipt set for
  repo-wide projection fan-out

## Invariants

- the event-kind registry and canonical envelope enum stay in exact active
  parity
- every admitted event kind names its payload owner and consuming stats
  summaries
- envelope admission does not transfer payload meaning to `aoa-stats`
- mirror copies remain subordinate to the canonical structural contract
- no event family is admitted from raw volume or an unowned telemetry label
- duplicate event ids retain the latest `(observed_at, event_id)` observation
- valid supersedes chains collapse to their latest descendant, while missing
  targets and cycles remain visible instead of being silently discarded
- loading and active-set resolution do not mutate source receipt objects

## Crosswalk

This part operates on stats source-family id `intake_contract`. The reciprocal
route is recorded in `stats/source_home.manifest.json` and
`mechanics/topology.json`.

## Current payload route

The filesystem-aware loading seam and deterministic resolution core live in
`src/aoa_stats_builder/receipt_abi.py`. Their focused governance and feed
proof is part-local. The published envelope, public validation command, and
root build facade remain compatibility surfaces, while the authored event-kind
registry belongs to `stats/intake-contract/`.
