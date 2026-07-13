# AOST-D-0012 Federated Measurement Ownership and Thin Access

## Index Metadata

- Decision ID: AOST-D-0012
- Original date: 2026-07-12
- Surface classes: stats/measurement-contract, stats/federation, src/core, mechanics/boundary-bridge, MCP/access
- Stats surfaces: measurement contract, measurement packet, local stats port, owner inventory, derived read contract
- Source lanes: active OS Abyss owner repositories, owner-local evidence, abyss-stack MCP services
- Guard families: derived-only authority, single-writer identity, statistical compatibility, privacy boundary, access-plane separation
- Posture: accepted

## Status

Accepted

## Context

The existing repository had become a strong collection of source-linked
observability summaries, but it did not yet define a general statistical
language that other OS Abyss owners could use. Dissolving those responsibilities
into eval, memory, KAG, runtime, SDK, or routing owners would leave no single
place to define cross-owner population, unit, aggregation, missingness,
uncertainty, provenance, and reporting compatibility. Centralizing all metric
meaning in `aoa-stats` would create the opposite failure: a derived organ would
absorb domain authority it cannot possess.

The repo-local MCP also mixed a stable read boundary with runtime transport and
registration. OS Abyss already places runnable MCP services under the
`abyss-stack` service topology.

## Decision

`aoa-stats` remains a distinct, derived, non-sovereign organ and owns the shared
statistical grammar, pure compatibility semantics, local-port protocol,
owner-level coverage inventory, and weaker cross-repo views. Every active
source owner gets a root `stats/` port unless its own boundary explicitly
routes the surface to a stronger owner. Each port owns its questions,
measurement identities, populations, dimensions, evidence handoffs, privacy,
freshness, and exports.

The source grammar lives under `stats/`; the filesystem-free implementation
lives under `src/` and remains subordinate to those contracts. Filesystem,
runtime, generated, and transport behavior stays at adapters. The stable read
contract remains owned by `aoa-stats`, while the runnable MCP implementation
will move to `abyss-stack/mcp/services/aoa-stats-mcp/`. The current repo-local
server remains the single temporary access plane only until verified consumer
cutover, after which it is removed rather than retained as a parallel service.

## Options Considered

- Dissolve stats into eval, memory, KAG, SDK, runtime, and routing owners:
  preserves local meaning but leaves cross-owner statistical compatibility and
  missingness behavior unowned.
- Centralize every metric and source feed in `aoa-stats`: simplifies discovery
  but transfers domain meaning, privacy decisions, and evidence authority to a
  weaker derived layer.
- Create a separate top-level `aoa-stats-mcp` repository: separates transport
  but gives a small runtime service an unnecessary owner boundary outside the
  existing stack service topology.
- Federate local meaning under one central compatibility contract and keep MCP
  as a stack-owned adapter: preserves both local authority and coherent access.

## Rationale

Statistics are useful across every owner class, but their meaning is local.
Compatibility is the reusable center: identity, population, unit, aggregation,
missingness, uncertainty, provenance, lifecycle, privacy, and reporting shape.
Owner questions and evidence are not reusable central truth. This split lets
cross-repo views remain reproducible without turning them into verdicts or
commands.

The MCP boundary follows the same logic. Semantic identity and authority
ceilings must survive transport changes, while installation, registration,
diagnostics, and lifecycle belong to the runtime stack. Keeping exactly one
active access plane avoids hidden ABI and registration drift.

## Consequences

- A local port can declare a meaningful measurement before it has a live
  producer without presenting absence as zero or current state.
- Cross-repo aggregation is allowed only when owners declare compatible axes,
  units, versions, populations, dimensions, and reporting rules.
- Existing read models remain useful derived views and migrate incrementally;
  they do not become the universal local-port template.
- The owner inventory must classify every active source owner and route
  significant non-source runtime surfaces without double counting.
- The statistical core must operate without MCP runtime.
- MCP cutover requires direct-versus-MCP semantic parity, consumer switch,
  removal of repo-local implementation, and one surviving registration.
- A port's presence, a count, a signal, or a score does not prove owner health,
  quality, causality, or permission to act.

## Source Surfaces

- `AGENTS.md`
- `DESIGN.md`
- `stats/measurement-contract/`
- `stats/federation/`
- `stats/source_home.manifest.json`
- `src/aoa_stats_builder/measurement.py`
- `mechanics/boundary-bridge/parts/measurement-packet-crossing/`
- `docs/BOUNDARIES.md`
- `docs/ARCHITECTURE.md`
- `stats/surface-catalog/CODEX_MCP.md`
- `src/aoa_stats_mcp/`

## Validation

Decision-lane checks are owned by [`AGENTS.md#verify`](AGENTS.md#verify).
Measurement, federation, source-home, and Boundary Bridge proof route through
their owning `AGENTS.md`, `VALIDATION.md`, and the root
[`AGENTS.md#verify`](../../AGENTS.md#verify) gate.
