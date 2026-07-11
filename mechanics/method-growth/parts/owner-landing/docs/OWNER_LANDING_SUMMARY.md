# Owner Landing Summary

## Purpose

`generated/owner_landing_summary.min.json` is the committed reference read
model for the Owner Landing receipt examples and their bounded stabilization
shape.

It exists so `aoa-stats` can preserve the public projection contract without
pretending that the example landings are current owner-local activity or final
owner truth.

## Input rule

The current committed build reads only the two event examples in
`stats/intake-contract/examples/session_harvest_family.receipts.example.json`:

- reviewed owner landing bundles carried by `reviewed_owner_landing_receipt`
- seed owner landing traces carried by `seed_owner_landing_trace_receipt`

Do not infer landing from seed staging alone, and do not reinterpret the
examples as receipts published by a current owner feed.

The deterministic transformation is the pure Method Growth core in
`src/aoa_stats_builder/candidate_lifecycle.py`. That core proves how admitted
receipts map into a summary; it does not prove that such receipts currently
exist.

## Questions answered

- how many landing examples the committed receipt chain represents
- which owner repos and owner shapes those examples name
- how often the represented posture is `early` or `thin-evidence`
- how often the represented outcome is `landed_owner_status`,
  `landed_owner_object`, `reanchored`, `merged`, `deferred`, or `dropped`

## Live posture

No real publisher or current receipt chain exists for the two Owner Landing
event kinds. The active profile therefore sets `live_state_capable: false`.
Live refresh omits the surface from `state/generated/` and the live catalog,
and removes any stale runtime copy even when the shared receipt feed is
non-empty.

Future live activation requires all of the following in one reviewed change:

- a named owner-local publisher
- current receipts backed by resolvable owner-local status surfaces
- a registered observation route that triggers refresh when those receipts
  change
- focused tests for admission, materialization, catalog membership, and stale
  cleanup

## Negative rules

Do not:

- emit one growth score
- infer proof from landing
- infer final object truth from owner-status landing alone
- mint owner meaning that belongs in `aoa-skills` or `Dionysus`
- treat committed receipt examples or pure-core tests as current live evidence
