# Stats read models

This branch is the authored source body behind the public summary-surface
catalog. Each active derived surface has one profile at
`active/<surface_name>.profile.json`; contract-only candidates live under
`deferred/`.

Profiles carry the stable question, derivation posture, stronger-owner inputs,
authority ceiling, public schema/output routes, consumer risk, live-state
posture, deterministic catalog order, and mechanics handoffs. The generated
catalog projects the public fields from these records. It is not an editable
copy of them.

`live_state_capable` is an executable selector, not a statement that every
committed surface is current. A `true` profile may be materialized and listed
by the local live refresh loop when its inputs resolve. A `false` profile stays
on its committed/reference route and is omitted from live output and the live
catalog, although refresh cleanup still removes any stale runtime copy.

The current managed inventory contains 25 active profiles; 21 are admitted to
live materialization. Continuity Window is one of the four reference-only
profiles. Its authored question describes the posture represented by the
committed aoa-agents example, experimental aoa-playbooks contract, aoa-memo
example, and aoa-evals catalog definitions. Those inputs do not constitute an
owner-runtime continuity artifact or receipt.

`surface-profile.schema.json` constrains both active and deferred source
records. Importable implementation stays under `src/aoa_stats_builder/`,
public schemas stay under `schemas/`, and public derived outputs stay under
`generated/`.

## Lifecycle

- `active/`: exactly the profiles emitted in
  `generated/summary_surface_catalog.min.json`.
- `deferred/`: bounded contract candidates that are not emitted as active
  surfaces.

Do not activate a deferred profile by moving the file alone. Its producer,
input chain, public schema/output, mechanic route, and validation must become
real in the same bounded change.
