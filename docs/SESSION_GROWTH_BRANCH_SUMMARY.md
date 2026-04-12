# Session Growth Branch Summary

## Purpose

`generated/session_growth_branch_summary.min.json` is the reviewed-only read
model for the next-kernel branch choices carried after reviewed closeout.

It exists so `aoa-stats` can show which bounded session-growth skill is being
recommended next without turning branch hints into route authority.

## Input rule

Read only:

- `decision_fork_receipt` payloads that carry reviewed followthrough hints such
  as `recommended_next_skill`, `reason_codes`, `owner_hypothesis`,
  `status_posture`, and `defer_allowed`

Plain fork-count receipts may still inform fork calibration, but they do not
automatically become branch-followthrough truth here.

## Questions answered

- which next kernel skills are being recommended after reviewed closeout
- how often defer remains an explicit honest outcome
- which owner targets receive the next bounded move
- which status postures are accumulating on those branch hints
- which reviewed reason codes recur across the current window

## Negative rules

Do not:

- infer branch truth from raw checkpoint notes
- replace `aoa-sdk` or `aoa-skills` ownership of why a branch exists
- invent route authority from branch counts
- collapse branch movement into one total score
