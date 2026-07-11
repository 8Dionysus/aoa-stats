# AGENTS.md

Route card for the `intake-contract` stats source family.

## Ownership

This family owns the shared stats receipt envelope, active event-kind
admission vocabulary, and the rule that makes source provenance and missing or
stale evidence visible to derivation.

It does not own the payload schemas or payload meaning carried inside the
envelope. Those remain with the source repositories named by the event-kind
registry. It also does not make receipt presence equivalent to proof,
workflow completion, route state, or current owner truth.

## Current source and public routes

- `stats/intake-contract/RECEIPT_ABI.md`
- `docs/BOUNDARIES.md`
- `schemas/stats-event-envelope.schema.json`
- `stats/intake-contract/event-kind-registry.json`
- `stats/intake-contract/examples/session_harvest_family.receipts.example.json`
- `mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json`

The registry and bounded fixture are canonical source records in this family.
The public envelope remains a root schema, while owner-local live-source
registration belongs to the recurrence mechanic.

## Implementation and validation

- implementation: `src/aoa_stats_builder/receipt_abi.py`,
  `scripts/build_views.py`, `scripts/refresh_live_stats.py`, and
  `scripts/check_live_publishers.py`
- validation: `scripts/validate_receipt_abi.py`,
  `mechanics/boundary-bridge/parts/receipt-abi-crossing/tests/test_receipt_abi_governance.py`,
  `mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py`,
  and `mechanics/recurrence/parts/live-receipt-refresh/tests/test_check_live_publishers.py`
- current read-only access: `src/aoa_stats_mcp/repo_state.py` and
  `src/aoa_stats_mcp/server.py`

## Mechanics crosswalk

- `mechanics/recurrence/parts/live-receipt-refresh`
- `mechanics/boundary-bridge/parts/receipt-abi-crossing`

The recurrence part owns repeatable refresh operation posture. The boundary
bridge part owns crossing and mirror-governance posture. Neither part may
absorb the envelope's source meaning or a source owner's payload authority.

## Change law

- Keep schema enum and active registry parity explicit.
- Preserve owner-repo attribution and evidence references.
- Do not turn missing input into zero, success, or absence.
- Route an operation change through the paired mechanic part.
- Route a payload-contract change to the source owner named by the registry.

## Verify

```bash
python scripts/validate_receipt_abi.py
python -m pytest -q mechanics/boundary-bridge/parts/receipt-abi-crossing/tests/test_receipt_abi_governance.py mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py mechanics/recurrence/parts/live-receipt-refresh/tests/test_check_live_publishers.py
```
