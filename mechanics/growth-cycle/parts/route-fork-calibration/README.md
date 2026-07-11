# route-fork-calibration

Summarizes `aoa-skills` `decision_fork_receipt` payloads into per-route
decision counts, explicit branch counts, option breadth, realized-outcome
link counts, evidence counts, and the latest observation time.

The authored meaning lives in
`stats/read-models/active/fork_calibration_summary.profile.json`; the stable
public contract and output remain
`schemas/fork-calibration-summary.schema.json` and
`generated/fork_calibration_summary.min.json`. Deterministic projection is
shared with the other Growth Cycle parts through
`src/aoa_stats_builder/growth_cycle.py`.
