# Automation Followthrough Summary

## Purpose

`generated/automation_followthrough_summary.min.json` is the bounded
follow-through read model for reviewed automation candidates.

It exists so `aoa-stats` can describe how often automation stays `not_now`,
reaches playbook-seed candidacy, or arrives at one reviewed real-run note
without pretending any of that is live schedule authority.

## Input rule

Read only:

- `automation_candidate_receipt` payloads that keep `seed_ready`,
  `checkpoint_required`, blocker codes, and optional bounded follow-through
  hints such as `playbook_seed_candidate` or `real_run_reviewed`

Do not infer scheduler activation from a seed example or from one stats window.

## Questions answered

- how many reviewed automation candidates exist in the current window
- how many are `seed_ready` versus still `not_now`
- how many still require an explicit checkpoint
- how many have reached a bounded playbook-seed candidate
- how many cite one reviewed real-run note
- which blocker codes recur most often

## Negative rules

Do not:

- infer a live schedule from `playbook_seed_candidate`
- outrank owner-local receipts or reviewed playbook evidence
- turn blocker counts into proof, policy, or operator authority
- collapse follow-through movement into one readiness score
