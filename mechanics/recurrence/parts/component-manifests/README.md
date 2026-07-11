# Component manifests

This part routes stats component recurrence declarations and their hook
companions as one bounded operation family.

## Status

- mechanic: `recurrence`
- stats source family: `surface_catalog`
- payload route: `part_localized`
- active contract: `CONTRACT.md`
- validation route: `VALIDATION.md`

Component declarations live under `manifests/components/`; hook declarations
live under `manifests/hooks/`. The projection schema, example, and recurrence
boundary docs are also part-local.

The part-local validator checks the exact eight component/hook pairs,
cross-file identity, current command and surface refs, and rejects former flat
root routes.
