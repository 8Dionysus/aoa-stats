# Contract

- Admit only `aoa-skills` `decision_fork_receipt` payloads registered by the
  stats intake contract.
- Count a next skill only when `recommended_next_skill`, or its
  `chosen_branch` fallback, names one of the bounded follow-through skills;
  unrecognized values remain absent rather than becoming new route truth.
- Preserve explicit owner targets, status postures, reason codes, and defer
  flags as counts. Do not infer them from plain fork volume or receipt order.
- Publish only the fields admitted by
  `schemas/session-growth-branch-summary.schema.json` at the stable route
  `generated/session_growth_branch_summary.min.json`.
- The result remains weaker than every owner-local route fork, playbook, and
  approval surface. It never becomes branch selection, routing, proof, gate,
  identity, or workflow truth.
