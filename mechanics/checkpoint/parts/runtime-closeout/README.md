# runtime-closeout

Publishes a bounded compatibility observation over historical runtime-wave
closeout receipts and keeps owner gates stronger.

## Routes

- deterministic core: `src/aoa_stats_builder/runtime_closeout.py`
- focused tests: `mechanics/checkpoint/parts/runtime-closeout/tests/`
- authored profile:
  `stats/read-models/active/runtime_closeout_summary.profile.json`
- public schema: `schemas/runtime-closeout-summary.schema.json`
- committed output: `generated/runtime_closeout_summary.min.json`

The current `abyss-stack` producer uses `runtime_trial_closeout_receipt` and a
different log name. This part does not reinterpret that new owner contract as
the older wave ABI.

This part owns its operation route and the localized payload roots declared in
`mechanics/topology.json`. Its stats source family owns the bounded meaning;
public schemas and generated outputs stay at their declared publication paths
when consumers depend on those paths.
