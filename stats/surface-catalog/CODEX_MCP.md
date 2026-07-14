# Stats MCP read contract

## Ownership

`aoa-stats` owns the transport-neutral meaning and authority ceiling of public
stats reads. The stack-owned `aoa-stats-mcp` service implements that contract;
the project Codex plane owns registration under the stable name `aoa_stats`.

The access plane is read-only and non-sovereign. It does not own a measurement,
owner-local definition, evidence, freshness, verdict, route, workflow, or
permission to act. The statistical core remains usable when MCP is absent.

## Public access shape

The read contract permits bounded access to:

- the owner-produced derived-surface catalog
- one catalog-listed surface with explicit reference or live-materialization
  posture
- the central authority and source-owner boundary references
- the federated owner inventory and one owner-local port definition
- compatibility findings for a caller-provided measurement contract and packet

Catalog and owner-port reads return owner-authored definitions or derived
projections, not attested truth. Packet checking reports compatibility only;
it preserves the same semantic identity as the direct packet reader without
attesting the packet's evidence or freshness.

Missing, stale, unknown, and reference-only states remain explicit. Access must
stay bounded and must not expose raw session material or sensitive owner
content.

## Owner routes

- Statistical semantics and direct read contract: `stats/measurement-contract/`
  and `scripts/read_measurement_packet.py`
- Catalog meaning and authority ceiling: `stats/surface-catalog/`
- Owner coverage and local-port compatibility: `stats/federation/`
- Runnable MCP service and exact tool surface:
  `abyss-stack/mcp/services/aoa-stats-mcp/`
- Project registration and wrapper: the Codex-plane owner in `8Dionysus`

The former repo-local MCP package, launcher, optional dependency, resources,
prompts, and live-source-registry access are retired. Reintroducing them would
create a second access implementation and violate the single-owner boundary.
