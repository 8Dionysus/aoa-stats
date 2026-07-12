# Documentation map

This directory contains repository-wide architecture, boundary, release,
decision, and historical surfaces. Operation-specific documentation lives with
its mechanic part and is discovered from the operation topology, not replayed
as a second part-by-part map here.

## Start here

- durable repository shape: [`../DESIGN.md`](../DESIGN.md)
- authored stats source home: [`../stats/README.md`](../stats/README.md)
- exact read-model state: [`../stats/read-models/README.md`](../stats/read-models/README.md)
- non-catalog operation contracts:
  [`../stats/operation-contracts/README.md`](../stats/operation-contracts/README.md)
- operation topology: [`../mechanics/README.md`](../mechanics/README.md) and
  [`../mechanics/topology.json`](../mechanics/topology.json)
- ownership boundary: [`BOUNDARIES.md`](BOUNDARIES.md)
- derived-view architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- current direction: [`../ROADMAP.md`](../ROADMAP.md) and
  [`../README.md#current-v0-surface`](../README.md#current-v0-surface)
- durable rationale: [`decisions/README.md`](decisions/README.md)
- release route: [`RELEASING.md`](RELEASING.md)

Follow a profile or operation record to its `mechanic_routes`, then read the
nearest mechanic and part route cards. Root documentation redirects are not
retained once active consumers and provenance point to the part-local owner.

## Repository-wide contracts

- surface strength: [`SURFACE_STRENGTH_MODEL.md`](SURFACE_STRENGTH_MODEL.md)
- read-only MCP access: [`../stats/surface-catalog/CODEX_MCP.md`](../stats/surface-catalog/CODEX_MCP.md)
- consumer regrounding: [`../stats/surface-catalog/CONSUMER_REGROUNDING.md`](../stats/surface-catalog/CONSUMER_REGROUNDING.md)

## History

`history/AGENTS_ROOT_REFERENCE.md` preserves the former long root guidance as
provenance. It is not an active instruction surface.
