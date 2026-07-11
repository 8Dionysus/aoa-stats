# Contract

- Admit only `aoa-skills` `decision_fork_receipt` payloads registered by the
  stats intake contract.
- Group by explicit `route_ref`, falling back to `session_ref`; preserve an
  absent `chosen_branch` as `unrecorded` rather than inventing a choice.
- Count option breadth only from a positive `branch_options_count` or the
  non-empty entries of `branch_ids`; count realized outcomes only from
  explicit `realized_outcome_refs`.
- Publish only the fields admitted by
  `schemas/fork-calibration-summary.schema.json` at the stable route
  `generated/fork_calibration_summary.min.json`.
- The result remains weaker than owner-local route selection and reviewed
  follow-through outcomes. It never becomes routing, outcome proof, gate,
  identity, or workflow truth.
