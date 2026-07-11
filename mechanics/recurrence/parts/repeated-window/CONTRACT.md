# Repeated window contract

## Purpose

Aggregate repeated receipt observations into bounded windows so recurrence is
visible without treating repetition as proof, promotion, or action authority.

## Inputs

- the authored `repeated_window_summary` profile under `stats/read-models/`
- active receipt envelopes admitted by the stats intake contract
- deterministic filesystem-free window rules in
  `src/aoa_stats_builder/repeated_window.py`
- the shared receipt object-identity helper from
  `src/aoa_stats_builder/object_observation.py`

## Output

`generated/repeated_window_summary.min.json`, validated by
`schemas/repeated-window-summary.schema.json`.

## Invariants

- repeated observations remain derived evidence, not owner truth
- a calendar-date bucket reports observed activity; it does not prove that
  change, repetition, cadence, or causality occurred
- a count or threshold does not authorize promotion or workflow activation
- superseded receipts do not silently re-enter the active window
- deterministic ordering is preserved across equivalent input orderings
- receipt, event-kind, object-identity, and evidence-ref counts are conserved
  within each window

## Crosswalk

This part operates on stats source-family id `read_models`. The source profile
owns the read-model meaning; the root schema and output remain its public
contract and publication route.
