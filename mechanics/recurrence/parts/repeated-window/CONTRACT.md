# Repeated window contract

## Purpose

Aggregate repeated receipt observations into bounded windows so recurrence is
visible without treating repetition as proof, promotion, or action authority.

## Inputs

- the authored `repeated_window_summary` profile under `stats/read-models/`
- active receipt envelopes admitted by the stats intake contract
- deterministic window rules in the shared builder

## Output

`generated/repeated_window_summary.min.json`, validated by
`schemas/repeated-window-summary.schema.json`.

## Invariants

- repeated observations remain derived evidence, not owner truth
- a count or threshold does not authorize promotion or workflow activation
- superseded receipts do not silently re-enter the active window
- deterministic ordering is preserved across equivalent input orderings

## Crosswalk

This part operates on stats source-family id `read_models`. The source profile
owns the read-model meaning; the root schema and output remain its public
contract and publication route.
