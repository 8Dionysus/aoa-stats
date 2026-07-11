# automation-followthrough

Summarizes `aoa-skills` `automation_candidate_receipt` payloads into two
bounded surfaces: per-pipeline readiness observations and window-level
follow-through counts.

The authored meanings live in
`stats/read-models/active/automation_pipeline_summary.profile.json` and
`stats/read-models/active/automation_followthrough_summary.profile.json`.
Their stable public contracts are
`schemas/automation-pipeline-summary.schema.json` and
`schemas/automation-followthrough-summary.schema.json`; matching output stays
at `generated/automation_pipeline_summary.min.json` and
`generated/automation_followthrough_summary.min.json`. Deterministic
projection is shared through `src/aoa_stats_builder/growth_cycle.py`.
