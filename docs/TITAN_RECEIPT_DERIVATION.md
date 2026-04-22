# Titan Receipt Derivation

## Purpose

Define derived observability for Titan-backed sessions without making stats a source of truth.

## Derived fields

```text
summon_count
active_default_roster_count
forge_gate_opened_count
delta_gate_opened_count
receipt_complete_count
receipt_incomplete_count
hidden_arena_violation_count
mutation_gate_violation_count
judgment_gate_violation_count
```

## Source

Stats are derived from session receipts and eval outputs. They do not define role meaning, memory truth, or seed canon.

## First-wave summary

The first wave is healthy when the default cohort appears explicitly, Forge and Delta remain gated, and receipts are complete.
