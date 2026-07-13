# Boundary bridge provenance

## Common mechanic

The parent mechanic is `Agents-of-Abyss/mechanics/boundary-bridge`. This
package records only the `aoa-stats` crossings evidenced by current contracts,
implementations, generated outputs, and tests.

## Current evidence routes

`receipt-abi-crossing` is evidenced by the canonical envelope schema, active
event-kind registry, governance doc, ABI validation implementation and command,
and focused governance plus feed-resolution tests listed through the stats
source crosswalk. The root build suite retains only repo-wide fan-out proof.

`consumer-regrounding` is evidenced by the retained public surface catalog,
schema, and compatibility validator plus the derived-signal precedence guide
and focused tests localized in its part. The former flat
`docs/DERIVED_SIGNAL_HYGIENE.md` route belongs to Git history, not active
compatibility.

`memory-owner-handoff` owns its focused contract, guide, and tests locally.
Its filesystem-free projection core lives at
`src/aoa_stats_builder/memory_movement.py`; its deterministic exact four-root
adapter and frozen bundle live at
`src/aoa_stats_builder/memory_movement_sources.py`. The root build script is a
compatibility and publication facade, while the authored profile retains the
public schema/output route and reference-only admission truth. The Cycle 9
false-live correction is about the missing refresh observation contract, not
about the authority of the reviewed `aoa-memo` corpus; rationale stays in
`docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md`.
`measurement-packet-crossing` is evidenced by the central measurement and
local-port schemas, the filesystem-free semantic core, the protocol validator,
and part-local tests derived from manual positive and negative trials. It owns
no owner metric or runtime access surface.

The topology declares the exact localized or mixed placement of all four
parts.

## Source-family crosswalk

- `receipt-abi-crossing` ↔ `stats` family `intake_contract`
- `consumer-regrounding` ↔ `stats` family `surface_catalog`
- `memory-owner-handoff` ↔ `stats` family `read_models`
- `measurement-packet-crossing` ↔ `stats` families `measurement_contract` and
  `federation`
