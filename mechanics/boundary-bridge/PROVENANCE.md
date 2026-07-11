# Boundary bridge provenance

## Common mechanic

The parent mechanic is `Agents-of-Abyss/mechanics/boundary-bridge`. This
package records only the `aoa-stats` crossings evidenced by current contracts,
implementations, generated outputs, and tests.

## Current evidence routes

`receipt-abi-crossing` is evidenced by the canonical envelope schema, active
event-kind registry, governance doc, ABI validation implementation and command,
and focused governance tests listed in `mechanics/topology.json`.

`consumer-regrounding` is evidenced by the retained public surface catalog,
schema, and compatibility validator plus the focused tests localized in its
part.

`memory-owner-handoff` owns its focused doc and tests locally while the
authored profile retains the public schema/output routes. All three parts now
use mixed localized/public placement declared exactly by the topology.

## Source-family crosswalk

- `receipt-abi-crossing` ↔ `stats` family `intake_contract`
- `consumer-regrounding` ↔ `stats` family `surface_catalog`
- `memory-owner-handoff` ↔ `stats` family `read_models`
