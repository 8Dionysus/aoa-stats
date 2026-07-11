# Contract

- Admit only `aoa-skills` `automation_candidate_receipt` payloads registered
  by the stats intake contract.
- For the pipeline view, group only by explicit `pipeline_ref`, then
  `manual_route_ref`, then `session_ref`, and count readiness flags and next
  artifact hints only when they are explicitly present.
- For the follow-through view, preserve explicit seed, checkpoint,
  playbook-seed, real-run-review, and blocker signals; a candidate without
  `seed_ready: true` remains `not_now`, not failed or rejected.
- Publish only the fields admitted by
  `schemas/automation-pipeline-summary.schema.json` and
  `schemas/automation-followthrough-summary.schema.json` at the stable routes
  `generated/automation_pipeline_summary.min.json` and
  `generated/automation_followthrough_summary.min.json`.
- The pipeline result remains weaker than owner-local approval, playbook, and
  runtime rollout surfaces; the follow-through result remains weaker than
  owner-local automation approval, runtime execution, and reviewed
  follow-through. Neither result becomes scheduler, routing, proof, gate,
  identity, or workflow truth.
