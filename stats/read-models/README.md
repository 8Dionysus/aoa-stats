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
