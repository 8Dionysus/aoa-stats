# Micro friction receipts

`aoa-stats` may consume micro friction receipts as derived observability.

Allowed contract surfaces:

- `schemas/micro_friction_receipt.schema.json`
- `schemas/micro_friction_recurrence.schema.json`
- `schemas/micro_friction_inbox.schema.json`

These surfaces summarize small friction notes, repeated friction patterns, and
bounded intake queues. They must not decide workflow meaning, proof meaning, or
playbook authority.

## Boundary

The stats layer may count, cluster, and surface friction signals.
It does not own the underlying owner-local meaning of the friction itself.
The inbox is a review aid, not a queue with governance power.
