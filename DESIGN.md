# aoa-stats design

## Role

`aoa-stats` is AoA's derived observability organ. It turns bounded,
source-owned evidence into deterministic read models without replacing the
sources that give that movement meaning.

## Thesis

Useful observability needs two structures:

- a source home that says what a stats object means
- mechanics homes that say how repeatable operations produce, refresh,
  validate, and publish that object

Keeping them cross-routed prevents both a flat repository where every
operation becomes root glue and an operation tree that absorbs the source
contracts it was meant to serve.

## Appearance

```text
aoa-stats/
├── stats/          source-authored stats meaning and family routes
├── mechanics/      repeatable operation packages and parts
├── src/            implementation libraries and access adapters
├── generated/      committed derived outputs
├── schemas/        stable published contract surfaces
├── scripts/        public, compatibility, and repo-wide entrypoints
└── tests/          repository and public-contract validation
```

Root publication districts remain legitimate by contract, not inertia. Their
authority comes from profiles, topology, route cards, and validators rather
than path depth.

## Anatomy

### The `stats/` source home

`stats/` owns source-authored semantics:

- receipt-envelope and event-kind admission meaning
- active, deferred, and retired read-model profiles
- bounded operation records for parts without a public catalog model
- catalog posture, authority ceilings, and source-to-operation handoffs
- the machine-readable source-family crosswalk

Profiles, rather than Python tables or generated catalogs, own public
read-model meaning. Operation records make non-catalog questions visible
without copying mechanic payload or inventing a fake surface. Runtime code
stays under `src/`; `stats/` is not an import package, output dump, receipt
store, or archive.

### The `mechanics/` operation home

`mechanics/` owns repeatable work around stats sources. Shared AoA mechanic
names are reused only when the operation has the same durable shape across
organs; stats-specific work becomes a local part under that parent.

A real part exposes an owner contract, payload or declared public route,
validation, and compatibility posture. Empty symmetry packages are not active.
The topology returns every active part to the stats family it serves.

### Implementation and publication districts

`src/aoa_stats_builder/` owns deterministic logic and source adapters.
`src/aoa_stats_mcp/` is a read-only access plane. `schemas/` and `generated/`
keep stable public paths.

Root `scripts/`, `tests/`, `docs/`, `examples/`, and `manifests/` contain only
repo-wide or explicit compatibility/public surfaces. Operation-owned config,
docs, examples, schemas, scripts, units, and focused tests live under the
nearest mechanic part.

## Authority surfaces

| Concern | Authoritative source |
| --- | --- |
| repository identity and edit route | root and nearest nested `AGENTS.md` |
| durable architecture | `DESIGN.md` |
| source-family map and root posture | `stats/source_home.manifest.json` |
| exact public surface state | target profile under `stats/read-models/` |
| non-catalog input maturity | target record under `stats/operation-contracts/` |
| active operation and placement | `mechanics/topology.json` and target part |
| material boundary rationale | source notes under `docs/decisions/` |
| compact consumer discovery | generated catalog and read models |

Entry README files are route atlases. They stay link-driven and do not carry
changing profile counts, named live/reference rosters, retirement chronology,
or mechanic-specific compatibility branches. Those facts remain discoverable
from their authoritative sources and generated decision indexes.

## Core, adapter, and proof boundaries

Pure receipt-to-read-model rules belong in `src/aoa_stats_builder/`.
Filesystem loading, workspace discovery, CLI policy, write/check mode, and
output fan-out stay at adapters and root entrypoints.

Shared implementation does not imply shared proof ownership:

- one part owns proof of behavior unique to its output
- package-level tests require a genuinely shared core and an explicit
  `package_payload_roots` declaration
- root tests prove repo-wide fan-out, public contracts, and compatibility
  integration rather than operation-specific branches

Compatibility applies to evidenced interfaces. A root CLI, builder, or alias
may remain stable while uncalled helper symbols are removed after current
caller, external-contract, and owner-part proof searches find none.
Migration-era documentation redirects use the same rule: re-ground active
consumer and provenance routes first, then retire the flat file rather than
preserving a permanent second entrypoint to an already part-local owner.

## Read-model lifecycle

Lifecycle is source-owned and asymmetric:

- `active/` records author public catalog surfaces and build fan-out
- `deferred/` records author evidence-gated candidates with explicit owner
  inputs, risk, and activation gaps
- `retired/` records are minimal cleanup/provenance tombstones with no builder,
  payload, catalog entry, or active mechanic claim

Catalog slots are stable identities, not dense positions. Retirement reserves
the former slot and does not keep an empty operation package alive.
Reintroduction is a new reviewed active-surface decision with current evidence,
a producer, a new reviewed slot, and validation.

Generated outputs remain weaker projections of this lifecycle. A generated
catalog is never the edit source merely because it is convenient to query.

## Live materialization

`live_state_capable` is authored source meaning, not an implementation
default. Live refresh derives its allowlist from active profiles and its stale
cleanup universe from active plus retired records.

Live admission requires both a current owner source and an observation route
that refreshes when the source changes. A resolvable adapter, committed
example, or static report is not enough for continuously advertised state.
Missing live input omits or cleans a surface; it never authorizes fallback to
an example or retired default.

## Operation

The refactor advances in alternating cross-slices:

```text
stats source family
        ↕ explicit crosswalk
mechanic route/part
        ↕
implementation + compatibility + generated output
```

One slice has one lead:

1. A stats-led slice strengthens one source-family contract and updates only
   the mechanics routes needed to keep it operable.
2. A mechanics-led slice names or localizes one evidenced operation and
   updates only the required source-family crosswalk.
3. The next slice changes the lead.

This rhythm keeps mechanics from becoming taxonomy without sources and keeps
`stats/` from becoming a design map without executable operations.

## Authority model

Stats facts are projections, not promotions:

- source repositories own receipts, verdicts, route state, memory, quests,
  runtime evidence, and domain meaning
- `aoa-stats` owns deterministic transformation and exact derived shape
- summaries may preserve upstream labels but cannot strengthen them
- missing, stale, rejected, or unregistered evidence remains visible
- evidence references are preferred over copied owner artifacts

## Shared mechanic vocabulary

Reuse only common AoA mechanics supported by current operations and payload.
A local operation is a part of a shared parent unless it proves a distinct
lifecycle, owner boundary, stop lines, and focused validation.

`mechanics/topology.json` is the active inventory. Documentation explains it
but cannot invent another package or part.

## Design principles

1. **Owner evidence before projection.** No read model outranks its source.
2. **Source meaning before operation convenience.** Mechanics serve stats
   contracts; they do not swallow them.
3. **One active home per payload.** Compatibility is explicit, not duplicated.
4. **Shared parent, local part.** Reuse common language only for a genuinely
   shared lifecycle.
5. **Cross-routed growth.** Every family can find its mechanic and every part
   can find its stats family.
6. **Determinism and visible freshness.** Staleness and absence stay visible.
7. **Thin access planes.** CLI, systemd, and MCP do not become owner truth.
8. **Thin entrypoints.** Route docs point to owners instead of replaying
   changing status.

## Good shape

- a source family names semantics and an authority ceiling
- its manifest points to implementation, output, and mechanic routes
- a mechanic part owns one coherent repeatable operation
- root entrypoints are canonical by declaration or thin compatibility
- validators check both directions of the crosswalk

## Bad shape

- creating packages only for visual symmetry
- treating every summary name as a top-level mechanic
- moving authored meaning under mechanics because a builder uses it
- keeping two active payload copies during migration
- allowing generated counts to exceed owner evidence
- copying a changing surface roster into root or family guidance

## Relationship to guidance

`AGENTS.md` is the operating route card. This document defines the durable
shape behind it. Nested cards narrow the law for a family, mechanic,
implementation, or compatibility district.

`ROADMAP.md` owns sequencing. `docs/decisions/` owns durable rationale when it
cannot be recovered from design and owner contracts. Generated indexes support
lookup but do not own decisions.

## Use by agents

Before changing structure, identify:

1. the source-owned fact being observed
2. the `stats/` family that owns derived meaning
3. the mechanic parent and part that own the operation
4. the current payload and compatibility consumers
5. the focused validator that proves the cross-contract

If one is unknown, make the route explicit before moving payload.
