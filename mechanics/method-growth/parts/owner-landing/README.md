# owner-landing

Summarizes `reviewed_owner_landing_receipt` and
`seed_owner_landing_trace_receipt` payloads into owner, posture, outcome, and
time-to-outcome observations.

The authored meaning lives in
`stats/read-models/active/owner_landing_summary.profile.json`; the stable public
contract and output remain `schemas/owner-landing-summary.schema.json` and
`generated/owner_landing_summary.min.json`. Deterministic projection is shared
through `src/aoa_stats_builder/candidate_lifecycle.py`.
