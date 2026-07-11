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

## Outputs

- an active or deprecated event-kind admission record
- a validated shared envelope shape
- mirror-parity findings for declared downstream copies

## Invariants

- the event-kind registry and canonical envelope enum stay in exact active
  parity
- every admitted event kind names its payload owner and consuming stats
  summaries
- envelope admission does not transfer payload meaning to `aoa-stats`
- mirror copies remain subordinate to the canonical structural contract
- no event family is admitted from raw volume or an unowned telemetry label

## Crosswalk

This part operates on stats source-family id `intake_contract`. The reciprocal
route is recorded in `stats/source_home.manifest.json` and
`mechanics/topology.json`.

## Current payload route

The focused governance test is part-local. The published envelope and public
validation command remain root compatibility surfaces, while the authored
event-kind registry belongs to `stats/intake-contract/`.
