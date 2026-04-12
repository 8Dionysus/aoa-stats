# Supersession Drop Summary

## Purpose

`generated/supersession_drop_summary.min.json` is one bounded read model for
visible pruning:

- supersession
- merge
- drop
- reanchor-after-drop

This is for turnover legibility, not for blame or ranking authority.

## Inputs

Read only:

- reviewed candidate-lineage entries carried by reviewed `harvest_packet_receipt` payloads
- reviewed owner landing bundles carried by `reviewed_owner_landing_receipt`
- seed owner landing traces carried by `seed_owner_landing_trace_receipt`

## Questions answered

- what is being replaced
- what is being dropped
- why discard happened when owner surfaces said so explicitly
- where reanchor replaced silent discard

## Negative rules

Do not:

- invent drop reasons when owner-local surfaces did not record them
- infer supersession from silence
- turn pruning counts into proof, workflow, or ranking authority
