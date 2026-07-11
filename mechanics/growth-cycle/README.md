# growth-cycle mechanic

`mechanics/growth-cycle/` is the active aoa-stats implementation of the common
`growth-cycle` mechanic.

Observes bounded session growth, branch calibration, and automation follow-through.

Start with `PARTS.md`, then use the selected part's `README.md`,
`CONTRACT.md`, and `VALIDATION.md`.

## Profile crosswalk

| Part | Authored profile | Owner input | Stable public contract and output |
| --- | --- | --- | --- |
| `route-fork-calibration` | `stats/read-models/active/fork_calibration_summary.profile.json` | `aoa-skills` `decision_fork_receipt` | `schemas/fork-calibration-summary.schema.json` and `generated/fork_calibration_summary.min.json` |
| `session-growth-branch` | `stats/read-models/active/session_growth_branch_summary.profile.json` | reviewed `aoa-skills` `decision_fork_receipt` follow-through hints | `schemas/session-growth-branch-summary.schema.json` and `generated/session_growth_branch_summary.min.json` |
| `automation-followthrough` | `stats/read-models/active/automation_pipeline_summary.profile.json` and `stats/read-models/active/automation_followthrough_summary.profile.json` | `aoa-skills` `automation_candidate_receipt` | `schemas/automation-pipeline-summary.schema.json`, `schemas/automation-followthrough-summary.schema.json`, and their matching `generated/*.min.json` surfaces |

The three parts share deterministic projection code in
`src/aoa_stats_builder/growth_cycle.py` and focused cross-part tests in
`mechanics/growth-cycle/tests/test_growth_cycle_projections.py`. The root
`scripts/build_views.py` remains the repo-wide build and compatibility facade.

Every output is descriptive. Route choice, reviewed follow-through,
automation approval, playbook state, and runtime execution stay with their
named owners.
