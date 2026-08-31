# AGENTS.md

Route card for the `stats/` source home.

## Scope and source-home law

`stats/` owns the source-authored meaning of stats families, including the
shared measurement grammar, local-port compatibility, intake admission,
derived-surface questions, lifecycle, and authority ceilings. It does not own
operation payloads, generated outputs, Python implementation, or source-owner
facts; those remain in the active routes named by `source_home.manifest.json`.

Keep only declared source records here: intake admission records, the bounded
intake fixture, active/deferred read-model profiles, retired cleanup tombstones,
and non-catalog operation records. Do not add executable payload, generated
JSON, owner-local feeds, or runtime state under `stats/`. One current payload
has one active owner.

## Conditional route

When a source-family question is known, use `source_home.manifest.json` to
select the family card and its authored record. When relevant to the route,
open the family README, then follow the named schema, owner port,
mechanic route, builder, or validator. Operation questions return to
`mechanics/topology.json` and the nearest part.

The six family routes are `measurement-contract/`, `federation/`,
`intake-contract/`, `read-models/`, `operation-contracts/`, and
`surface-catalog/`. This list is a stable source-home crosswalk; changing
membership belongs in the manifest, not this card. Do not hand-maintain mutable
surface counts or named rosters here.
These route cards do not hand-maintain mutable status rosters.

## Lifecycle and authority

- `measurement-contract/` owns portable statistical shape; owner repositories
  retain metric meaning.
- `federation/` owns local-port compatibility and owner-level coverage.
- `intake-contract/` owns the shared envelope and event-kind admission below
  source payload authority.
- `read-models/` owns active/deferred profiles and retired tombstones.
- `operation-contracts/` owns bounded non-catalog questions and owner return.
- `surface-catalog/` owns compact discovery and consumer caution posture.

Active profiles may be materialized live only when their source meaning and an
observation route both exist. Deferred profiles remain evidence-gated;
retired profiles publish no surface and reserve their former catalog slots.
Generated, compact, MCP, adapter, and runtime surfaces remain weaker than
authored sources and owner-local facts. Missing, stale, rejected, and
unregistered evidence stays visible.

## Cross-route boundary

Every family route names its meaning, source and public contracts, existing
implementation and validation routes, generated/access companions, mechanic
handoffs, and authority ceiling. Change source meaning with its reciprocal
mechanic route; do not copy source meaning into mechanics or generated output.
`stats/source_home.manifest.json` is the machine-readable source-family
crosswalk; README files explain it but do not override it.

## Conditional validation and closeout

Use root `VALIDATION.md` for source-home and protocol route selection, then the
focused family or mechanic-part validation named by the manifest. Regenerate
declared projections from authored inputs. Report source family, owner inputs,
reciprocal mechanic, output shape, evidence class, and remaining stronger-owner
or freshness boundary.
