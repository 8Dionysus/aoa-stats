# aoa-stats design

## Role

`aoa-stats` is the central statistical measurability organ of OS Abyss. It
defines compatible measurement semantics, federates owner-local `stats/`
ports, and turns bounded source-owned evidence into deterministic read models
without replacing the sources that give that movement meaning.

## Thesis

Useful statistical observability needs two structures:

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
├── skills/         admitted owner-local callable procedure source
├── src/            implementation libraries and access adapters
├── generated/      committed derived outputs
├── schemas/        stable published contract surfaces
├── scripts/        public, compatibility, and repo-wide entrypoints
└── tests/          repository and public-contract validation
```

Root publication districts remain legitimate by contract, not inertia. Their
authority comes from profiles, manifests, topology, route cards, decisions,
and validators rather than path depth.

## Anatomy

### The `stats/` source home

`stats/` owns source-authored semantics:

- the portable measurement and packet grammar
- the local-port contract and owner-level coverage inventory
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

### Statistical model

The central model separates six things that are often collapsed:

- an event or trace records one occurrence
- a measure or metric defines what is measured and by which unit
- a statistic describes a population, sample, cohort, or window
- a reporting view applies a named and versioned presentation rule
- a bounded signal supports analysis or triage without becoming proof
- an eval verdict or routing decision remains with its stronger owner

The source contract makes observation and metric identity, single-writer
owner, population, sample, cohort, window, value, unit, dimensions,
cardinality, numerator and denominator, aggregation, temporality, lifecycle,
compatibility, missingness, uncertainty, provenance, reporting rule, privacy,
and live/reference posture explicit.

`pass_at_k` means at least one success among `k`; `pass_all_k` is the portable
identifier for `pass^k`, where all selected attempts succeed. Ratios retain
their components. Distributions and quantiles retain represented sample and
population. `missing`, `unknown`, and `stale` do not become zero or fail.

### Federation

Every active source owner receives a root `stats/` port unless an explicit
owner boundary routes the surface to a stronger owner. The central local-port
schema owns compatibility only. A local port owns its questions, measurement
definitions, populations, dimensions, evidence handoffs, privacy and freshness
posture, and real exports.

`stats/federation/owner-inventory.json` is the durable coverage map. It names
portable owner routes, never host paths, worktree state, or session history.
Significant deployed or runtime surfaces that are not independent source
owners are routed rather than counted twice.

### The `mechanics/` operation home

`mechanics/` owns repeatable work around stats sources. Shared AoA mechanic
names are reused only when the operation has the same durable shape across
organs; stats-specific work becomes a local part under that parent.

A real part exposes an owner contract, payload or declared public route,
validation, and compatibility posture. Empty symmetry packages are not active.
The topology returns every active part to the stats family it serves.

### The `skills/` callable interface

`skills/aoa-stats/SKILL.md` is one repository-owned callable bundle with
internal `answer`, `diagnose`, and `evolve` modes. It routes an agent through
the existing stats and mechanics owners; it does not duplicate their meaning,
payload, proof, or implementation. One managed OS user-profile copy exposes it
to Codex and never outranks the canonical source.

The home admits no generic shared bundles and no experimental modes as separate
prompt-visible skills. A split requires held-out evidence of independent
trigger, ABI, composition value, and outcome benefit.

### Implementation and publication districts

`src/aoa_stats_builder/measurement.py` is a filesystem-free executable
interpretation of the measurement source contracts. Existing derived-view
modules contain bounded pure projections; source discovery and loading remain
adapters. `stats/surface-catalog/CODEX_MCP.md` owns the transport-neutral read
contract, while the stack-owned `aoa-stats-mcp` owns MCP transport and service
lifecycle. `schemas/` and `generated/` keep stable public paths.

Root `scripts/`, `tests/`, `docs/`, `examples/`, `manifests/`, and `skills/`
contain only repo-wide, explicit compatibility/public, or admitted callable
surfaces. Operation-owned config, docs, examples, schemas, scripts, units, and
focused tests live under the nearest mechanic part.

### Existing-surface classification

The current repository is classified by authoritative route rather than a
second hand-maintained file roster:

- measurement, federation, and receipt-envelope schemas are fundamental shared
  contracts
- active read-model profiles are concrete derived-view contracts; deferred
  profiles are evidence-gated domain candidates; retired profiles are obsolete
  publication tombstones retained only for cleanup and provenance
- filesystem-free projection modules are bounded cores for their views, while
  `*_sources.py`, workspace discovery, refresh, and build fan-out are domain or
  infrastructure adapters
- files under `generated/` are generated projections, never edit sources
- `skills/aoa-stats/SKILL.md` is the admitted callable source; the OS profile
  installs one derived user copy and this repository creates no duplicate
- examples and committed snapshots remain reference surfaces unless an authored
  profile and observable producer admit them to live state
- ignored `state/`, systemd, and deployment material are runtime-only surfaces
- MCP runtime implementation belongs to the stack-owned `aoa-stats-mcp`; this
  repository retains only its statistical read contract
- root wrappers are compatibility surfaces only when topology names a current
  consumer; unsupported wrappers and empty read models remain retired rather
  than preserved as legacy

This route-based classification covers new families without creating another
mutable object inventory. A surface that fits none of these classes must first
acquire an owner and consumer or be removed as repetition or overcode.

## Authority surfaces

| Concern | Authoritative source |
| --- | --- |
| repository identity and edit route | root and nearest nested `AGENTS.md` |
| durable architecture | `DESIGN.md` |
| shared statistical grammar | `stats/measurement-contract/` |
| local-port protocol and owner coverage | `stats/federation/` |
| source-family map and root posture | `stats/source_home.manifest.json` |
| exact public surface state | target profile under `stats/read-models/` |
| non-catalog input maturity | target record under `stats/operation-contracts/` |
| active operation and placement | `mechanics/topology.json` and target part |
| repository callable procedure | `skills/aoa-stats/SKILL.md` and `skills/port.manifest.json` |
| stable derived-view layering | `docs/ARCHITECTURE.md` |
| material boundary rationale | source notes under `docs/decisions/` |
| compact consumer discovery | generated catalog and read models |

Entry README files are route atlases, and the public architecture document is
a stable derived-view contract. They stay link-driven and do not carry changing
profile counts, named live/reference rosters, retirement chronology,
part-by-part operation inventories, or mechanic-specific compatibility
branches. Those facts remain discoverable from their authoritative sources,
the topology, and generated decision indexes.

Repo-wide validation owns stable entrypoints and delegates membership checks to
the source manifest, mechanics topology, and focused part proof. A hand-picked
list of family or part documents inside a root validator is another mutable
inventory and is not authoritative.

Mechanic package activation follows the same single-source rule. The topology
owns the machine-readable package set, the root directory materializes it, and
tests prove parity without freezing current package names in another constant.

The root roadmap is a sequencing surface, not another inventory. It may name
durable priorities and the alternating stats/mechanics rhythm, while exact
surface state, operation membership, and shipped chronology remain with
profiles, topology, generated discovery, decisions, and the changelog.

## Core, adapter, and proof boundaries

Shared statistical meaning belongs in the schemas under
`stats/measurement-contract/`. Their pure cross-field implementation and
receipt-to-read-model rules belong in `src/aoa_stats_builder/`. Filesystem
loading, workspace discovery, CLI policy, write/check mode, output fan-out,
runtime registration, and MCP transport stay at adapters and entrypoints.

The pure measurement core may validate compatibility, preserve evidence and
semantic identity, summarize privacy-bounded distributions, compute exact
finite-sample pass statistics, and aggregate only along owner-declared axes.
It does not discover repositories, read owner files, publish state, or decide
what a local metric means.

Shared implementation does not imply shared proof ownership:

- one part owns proof of behavior unique to its output
- package-level tests require a genuinely shared core and an explicit
  `package_payload_roots` declaration
- root tests prove repo-wide fan-out, public contracts, and compatibility
  integration rather than operation-specific branches

Family-level proof discovery derives focused test owners from topology and
part-local test districts. It checks that each declared district is reachable
from the source family without maintaining a second map of current part names
and filenames.

The root build integration derives its expected output set from active profiles
and checks complete committed-byte parity. Field-level meaning, example values,
and projection invariants stay with the mechanic that owns each output.
Consumer return-route assertions and catalog artifact trust-lifecycle proof are
also mechanic-owned; the root catalog test constrains only the authored/public
catalog contract shared across those operations.

Compatibility applies to evidenced interfaces. A root CLI, builder, or alias
may remain stable while uncalled helper symbols are removed after current
caller, external-contract, and owner-part proof searches find none.
Relocated owner references follow the same rule: current authored inputs point
to one canonical owner path, and a temporary translation disappears after
consumer re-grounding. A committed or reference-only surface still resolves
its exact declared source; its weaker publication posture does not authorize a
stale path or fallback.
Migration-era documentation redirects use the same rule: re-ground active
consumer and provenance routes first, then retire the flat file rather than
preserving a permanent second entrypoint to an already part-local owner.
Cross-owner derived-signal precedence belongs to the Boundary Bridge operation
that applies the return-to-owner rule, while repository-wide architecture keeps
only the stable authority ladder.

Profile vocabulary is source meaning. Its human contract lives with the
owning stats family and is checked against authored profiles; root architecture
may link it but does not own a duplicate document or named current-surface
posture.

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

Validators derive lifecycle membership from the authored profile directories
and compare their public projections with the catalog. They may enforce a
non-empty active family and exact slot uniqueness, but do not freeze current
active, deferred, or retired cardinalities as validator constants.

The same growth rule applies to non-catalog operations. Their active inventory
is the non-empty set of authored operation records with exact reciprocal links
through the source manifest and mechanics topology; the current number of
parts is not a repository ABI.

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

The live-refresh mechanic owns the set algebra and failure behavior, not a
second inventory: admission is derived from active profiles, cleanup from
active profiles plus retired tombstones, and catalog membership from outputs
actually materialized. Exact members and cardinalities are read from the
authored profiles by runtime code and part-local proof instead of being copied
into mechanic documentation or root documentation tests.

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

The same ladder governs local ports: the owner writes the measurement identity
and evidence; `aoa-stats` checks compatibility and derives a weaker view; MCP,
KAG, dashboards, and caches expose that view without gaining its authority.

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
9. **Federated meaning.** Central compatibility does not absorb local metric
   meaning.
10. **Explicit absence and uncertainty.** Missingness, freshness, sample size,
    and uncertainty survive every projection.

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
