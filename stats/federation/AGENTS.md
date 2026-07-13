# AGENTS.md

Route card for the federated local-port contract and inventory.

## Scope

This branch owns the compatibility shape and canonical inventory for root
`stats/` ports across active OS Abyss owner repositories. It does not own any
local question, measurement, evidence, privacy decision, or export.

Read `README.md`, then `local-port.schema.json` and
`owner-inventory.schema.json`. Follow each inventory entry to the owner before
changing its classification or port.

## Owner law

- Inventory entries describe durable owner routes, never host-specific paths or
  one-session work state.
- `implemented` requires an existing owner-local port or the central source
  home; `routed_to_stronger_owner` requires an explicit stronger-owner route.
- A local port references the central schemas and authors only its own domain
  meaning.
- Missing ports remain visible. An owner exception is explicit and uncommon.

## Stop lines

Do not copy owner manifests, evidence, runtime state, raw sessions, migration
notes, or current worktree status here. Do not infer owner health from port
presence.

## Verification

The executable owner is `scripts/release_check.py`; cross-repo compatibility
proof is added only after owner-local manual journeys establish its invariants.
