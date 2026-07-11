# Consumer regrounding

This part routes derived catalog and intake-coverage signals that tell a
consumer when to return to stronger owner-local sources.

## Status

- mechanic: `boundary-bridge`
- stats source family: `surface_catalog`
- payload route: `mixed localized/public`
- active contract: `CONTRACT.md`
- validation route: `VALIDATION.md`

Focused tests live in this part. The public catalog schema/output and thin
downstream-canary command remain at the root paths listed in
`mechanics/topology.json`.
