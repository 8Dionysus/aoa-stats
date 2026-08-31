# AGENTS.md

Route card for the `intake-contract` stats source family.

## Ownership

This family owns the shared stats receipt envelope, active event-kind
admission vocabulary, and the provenance-preserving rule that makes missing or
stale evidence visible to derivation. It does not own payload schemas or
payload meaning carried inside the envelope; source repositories retain those
facts. Receipt presence is not proof, workflow completion, route state, or
current owner truth.

## Conditional source routes

When intake admission is the selected question, follow the shared stats receipt
envelope, `RECEIPT_ABI.md`, the event-kind registry, and the bounded fixture.
The public envelope remains a root schema; live-source registration belongs to
the recurrence mechanic. The implementation routes are the receipt ABI,
refresh, and publisher adapters named by the source-home manifest.

The `Mechanics crosswalk` is the recurrence live-refresh part and the Boundary
Bridge receipt-ABI crossing part. Neither part absorbs envelope meaning or a
source owner's payload authority.

## Change law

- Keep schema enum and active registry parity explicit.
- Preserve owner-repo attribution and evidence references.
- Do not turn missing input into zero, success, or absence.
- Route operation changes through the paired mechanic part and payload changes
  to the source owner named by the registry.
- Keep validation procedure in the root or nearest part `VALIDATION.md`.

## Conditional validation and closeout

Use the root `VALIDATION.md` for receipt-ABI and shared protocol selection,
then the focused crossing or live-refresh route. Report event-family admission,
source refs, missingness, owner handoff, and whether evidence is fixture,
committed, or live.
