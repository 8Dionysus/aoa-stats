# Owner Landing Summary

## Purpose

`generated/owner_landing_summary.min.json` is the reviewed-only read model for
first owner landings and later bounded stabilization.

It exists so `aoa-stats` can show where a growth-refinery candidate has landed
in owner-local status space without pretending that landing is final owner
truth.

## Input rule

Read only:

- reviewed owner landing bundles carried by `reviewed_owner_landing_receipt`
- seed owner landing traces carried by `seed_owner_landing_trace_receipt`

Do not infer landing from seed staging alone.

## Questions answered

- how many reviewed candidates landed in owner-local status surfaces
- which owner repos and owner shapes are receiving them
- how often landings are still `early` or `thin-evidence`
- how often the observed landing outcome becomes `landed_owner_status`,
  `landed_owner_object`, `reanchored`, `merged`, `deferred`, or `dropped`

## Negative rules

Do not:

- emit one growth score
- infer proof from landing
- infer final object truth from owner-status landing alone
- mint owner meaning that belongs in `aoa-skills` or `Dionysus`
