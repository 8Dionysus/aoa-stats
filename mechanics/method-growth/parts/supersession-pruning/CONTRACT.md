# Contract

- Derive turnover only from explicit `drop_reason`, `merged_into`,
  `superseded_by`, `supersedes`, or reanchor signals in admitted receipts.
- Do not infer rejection, replacement, merge, or causal rationale from owner
  changes, missing stages, time order, or receipt absence.
- Keep owner-repo counts descriptive and preserve the distinction between a
  candidate being superseded and a candidate replacing another.
- Publish only the fields admitted by
  `schemas/supersession-drop-summary.schema.json` at the stable route
  `generated/supersession_drop_summary.min.json`.
- The result remains weaker than reviewed turnover records and never becomes
  pruning policy, owner acceptance, routing, proof, gate, or workflow truth.
