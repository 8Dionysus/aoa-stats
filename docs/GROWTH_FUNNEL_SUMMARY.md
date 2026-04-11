# Growth Funnel Summary

## Purpose

`aoa-stats` exposes one bounded derived growth-refinery surface:

- `generated/candidate_lineage_summary.min.json`

This surface exists to show how reviewed candidates move through the refinery
without turning stats into routing authority, proof authority, or seed truth.

## Input boundary

The v1 summary reads only reviewed owner-local receipts.

For the first slice, that means reviewed lineage entries carried on
`harvest_packet_receipt` payloads.

Raw checkpoint notes do not enter this summary.
Provisional carry may influence the reviewed receipt, but stats does not read
that provisional layer directly.

## Funnel stages

The funnel stays explicit:

`observed -> checkpointed -> reviewed -> harvested -> seeded -> planted -> proved -> promoted -> superseded_or_dropped`

Counts stay derived from the strongest stage evidence actually present on the
reviewed receipt payload.

## Required lenses

The v1 summary carries:

- counts by stage
- counts by owner target
- counts by owner shape
- status posture counts
- time-to-stage medians
- misroute aggregates
- supersession aggregates
- axis-pressure aggregates

## Negative rules

Do not:

- emit one total growth score
- infer `seeded` from reviewed harvest alone
- infer `planted` from seed staging alone
- outrank owner receipts
- outrank eval verdicts
- pull raw checkpoint notes into stats

## Extension posture

Later receipts may make `seeded`, `planted`, `proved`, and `promoted` visible.

That later extension should still keep the same rule:
owner-local reviewed receipts first, derived stats second.
