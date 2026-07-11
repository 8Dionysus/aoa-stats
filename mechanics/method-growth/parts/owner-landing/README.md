# owner-landing

Summarizes committed `reviewed_owner_landing_receipt` and
`seed_owner_landing_trace_receipt` examples into owner, posture, outcome, and
time-to-outcome observations. The current public output is a bounded reference
snapshot; no owner-local publisher or current receipt chain exists for either
event kind.

The authored meaning lives in
`stats/read-models/active/owner_landing_summary.profile.json`; the stable public
contract and output remain `schemas/owner-landing-summary.schema.json` and
`generated/owner_landing_summary.min.json`. Deterministic projection is shared
through the filesystem-free core in
`src/aoa_stats_builder/candidate_lifecycle.py`.

The authored selector is therefore `live_state_capable: false`. Live refresh
must omit Owner Landing from `state/generated/` and its live catalog, and must
remove any stale runtime copy. Future activation requires a real named owner
publisher, current receipts for the accepted event kinds, and a tested
registry/watch route that observes those receipts when they change.
