# aoa-stats design

## Role

`aoa-stats` is AoA's derived observability organ. It turns bounded,
source-owned evidence into deterministic read models that help humans and
tools see movement without replacing the sources that give that movement
meaning.

## Thesis

Useful observability needs two different kinds of structure:

- a source home that says what a stats object means
- mechanics homes that say how repeatable operations produce, refresh,
  validate, and publish that object

Keeping those structures cross-routed prevents two common failures: a flat
repository where every operation becomes root-level glue, and an operation
tree that quietly absorbs the source contracts it was meant to serve.

## Appearance

At maturity, the repository should read as:

```text
aoa-stats/
├── stats/          source-authored stats meaning and family routes
├── mechanics/      repeatable operation packages and parts
├── src/            implementation libraries and access adapters
├── generated/      committed derived outputs
├── schemas/        compatibility and published contract surfaces
├── scripts/        public, compatibility, and repo-wide entrypoints
└── tests/          repository and public-contract validation
```

Root publication districts remain legitimate by contract, not by inertia.
Their authority is determined by authored profiles, topology, and route cards,
not by path depth alone.

## Anatomy

### The `stats/` source home

`stats/` owns source-authored semantics:

- the receipt admission registry and bounded fixture used to exercise the
  shared envelope
- one profile per active or deferred read model under `stats/read-models/`
- one authored source record per part-local observation contract that
  deliberately does not publish a catalog profile under
  `stats/operation-contracts/`
- the families of read models this organ can honestly produce
- the dimensions, windows, freshness states, and authority ceilings those
  models use
- the relationship between a family and its implementation, compatibility,
  generated-output, and mechanics routes

The read-model profiles, rather than a Python constant table, are the source
of the public catalog projection. They name the public schema/output routes,
stronger-owner inputs, authority ceiling, lifecycle, deterministic order, and
mechanics handoffs. Runtime code continues to live under `src/`; `stats/` is
not a second Python package, an output dump, or an archive.

Part-local observation contracts remain visible through
`stats/operation-contracts/` when they have real mechanics payload but no
public catalog surface. Each source record owns only the bounded stats
question, evidence posture, authority ceiling, consumer risk, and return to
stronger owners. The mechanic part remains the sole owner of schemas,
examples, scripts, tests, and generated payload. This keeps the crosswalk
complete without inventing fake surface profiles or a shadow mechanics tree.

### The `mechanics/` operation home

`mechanics/` owns repeatable work around stats sources. Shared AoA mechanic
names are reused when the operation has the same durable shape across organs;
stats-specific work normally becomes a local part under that shared parent.

A real mechanic part makes its contract, payload or declared public surface,
validation, and compatibility posture discoverable. Empty symmetry packages
are not active mechanics.

### Implementation and compatibility districts

`src/aoa_stats_builder/` and `src/aoa_stats_mcp/` remain implementation and
access homes. Root `schemas/` and `generated/` are stable public publication
districts. Root `scripts/`, `tests/`, `docs/`, `examples/`, and `manifests/`
contain only repo-wide or explicit compatibility surfaces. Operation-local
config, docs, examples, manifests, schemas, scripts, systemd templates, and
focused tests live with the mechanic part that owns them.

When one deterministic importable core serves several parts of the same
mechanic, its shared focused test may live at the mechanic-package level only
through an explicit `package_payload_roots` declaration in
`mechanics/topology.json`. Part-specific payload and validation stay with the
nearest part.

The current Method Growth, Growth Cycle, and Audit observation cores follow
this shape: pure receipt-to-read-model transformations live in
`src/aoa_stats_builder/`, shared cross-part behavior is tested with the mechanic
package, and `scripts/build_views.py` remains the repo-wide input, fan-out, and
publication facade. Audit keeps a shared core only for core-skill application
and surface-strength detection because both use the same finish-stage receipt
selector. Object observation has a separate core and part-local test boundary
because it summarizes every admitted event kind. Neither implementation gains
audit, routing, or proof authority.

Route Progression follows the single-part variant of the same architecture.
Its stats profile owns the bounded question, reference posture, exact
stronger-owner chain, and authority ceiling. A filesystem-free RPG core may
project the committed legacy numeric receipt shape, while the part-local test
district owns behavioral proof and `scripts/build_views.py` keeps only
compatibility aliases and repo-wide fan-out. The RPG center retains vocabulary
and stop-lines, `aoa-agents` retains the agent-layer overlay, `aoa-sdk` retains
typed transport, and `aoa-skills` retains receipt truth. The current semantic
`axis_delta_summary` contract is deliberately not converted into numeric
totals, so Route Progression stays outside live state until a non-invented
cross-owner projection contract exists.

The first consumer return target is the exact current semantic schema and
example in `aoa-skills`. Compatibility-fixture wording remains in the
reference derivation posture only; it must not masquerade as stronger current
owner truth or make a router prefer the legacy numeric shape.

Runtime Closeout follows the mechanics-led Checkpoint variant. A pure
Checkpoint core owns only the historical receipt-to-summary transformation;
the profile owns the reference/live posture and stronger-owner route; the root
builder keeps compatibility aliases and repo-wide fan-out. `abyss-stack`
currently writes `runtime_trial_closeout_receipt` to
`runtime-trial-closeouts.jsonl`, while the admitted stats ABI and installed
observation route still name the older wave receipt and feed. The active stats
source registry excludes that historical feed, while the compatibility ABI
continues to support the committed fixture. The projection therefore stays
committed/reference-only until a cross-owner change chooses a canonical
receipt kind, registers it, observes its real feed, and proves a current
producer. Extraction does not authorize an implicit kind conversion.

Generated artifacts never become source authority merely because they are
committed or convenient to query.

Local live state is an authored-profile projection, not a second hardcoded
output inventory. The live refresh mechanic materializes only active profiles
with `live_state_capable: true`, publishes a catalog for the surfaces actually
materialized, and cleans stale files across the full managed profile set.
For Component Refresh specifically, the reviewed-example adapter may build the
committed public snapshot but is excluded from live mode until a real
owner-runtime source exists. The selector admits a profile; it does not by
itself certify the provenance declared by other `true` profiles.

Continuity Window is a separate audited reference boundary. Its committed
adapter may read the committed cross-owner example chain, but a filesystem-free
core must validate continuity, revision, reanchor, anchor, playbook, memo, and
eval coherence before projection. A status such as `reanchored` cannot
manufacture a successful-reanchor count; only explicit timeline evidence can.
Until an owner-runtime continuity artifact or receipt exists, the surface stays
absent from local live materialization.

Codex Plane Deployment is the stats-led counterpart. Its committed snapshot
may derive from owner-authored rollout examples, but those examples are not
current deployment evidence. The projection core must be filesystem-free, and
the source adapter must expose separate `reference` and `live` entry paths.
Live mode reads only the three deploy-local trust, regeneration, and rollout
artifacts from an explicit workspace root, never falls back to examples, and
omits or cleans the optional surface when that runtime chain is absent. The
authored profile remains non-live until the real producer, artifacts, and
refresh trigger are proven together.

Trusted Rollout History is a separate mechanics-led release-support boundary.
It consumes exactly the four checked-in owner-history surfaces under
`8Dionysus/generated/codex/rollout/`, validates their lifecycle and reference
coherence in a filesystem-free core, and projects the operations and drift
companions without treating a reviewed historical latest record as current
workspace state. Its source adapter is committed-history only; it has no live
fallback and no deployment-trio responsibility.

Rollout Cadence is a third, deliberately separate source context. The campaign,
drift-review, and rollback-followthrough examples form one immutable
owner-example bundle, but the resulting operations keep their mechanic
owners: campaign projection belongs to release support and drift review belongs
to audit. Shared validation may be reused across those projections without
merging their operation ownership or promoting examples into checked-in
history. Both cadence profiles remain reference-only until a real cadence
producer and refresh route exist.

Live admission is an atomic source-and-observation boundary. A source may be
authentic owner truth and still be unsuitable for continuously advertised
local state when no refresh trigger observes it. Memory Movement therefore
keeps its reviewed `aoa-memo` corpus adapter and committed snapshot, while its
live selector stays closed until catalog, object, reviewed-intake, and landing
movement can trigger refresh through an explicit contract. Owner Landing stays
reference-only while its event kinds have no real publisher, and Stress
Recovery stays reference-only while its eval is draft and its only resolvable
report is an example. Their committed summaries remain useful bounded contract
snapshots; absence from `state/generated/` is the honest runtime posture.

## Operation

The refactor advances in alternating cross-slices:

```text
mechanic route/part
        ↕ explicit crosswalk
stats source family
        ↕
implementation + compatibility + generated output
```

One slice has one lead:

1. A mechanics-led slice names or localizes one repeatable operation and
   updates only the necessary source-family crosswalk.
2. A stats-led slice strengthens one source-family contract and updates only
   the mechanics routes needed to keep it operable.
3. The next slice changes the lead.

This alternating rhythm is part of the architecture. It keeps mechanics from
becoming a taxonomy without sources, and keeps `stats/` from becoming a design
map without executable operations.

## Authority model

Stats facts are projections, not promotions of authority.

- Source repositories own their receipts, verdicts, route state, memories,
  quests, runtime evidence, and domain meaning.
- `aoa-stats` owns the deterministic transformation and the exact shape of its
  derived read models.
- A summary may preserve an upstream authority or confidence label, but cannot
  strengthen it.
- Missing, stale, rejected, or unregistered evidence remains observable as
  such; it is not silently converted into zero, success, or absence.
- Evidence references are preferred over copies of owner artifacts.

## Shared mechanic vocabulary

AoA organs repeat a common mechanic vocabulary. `aoa-stats` should reuse only
the subset supported by current operations and payloads. A local operation is
a part of a shared parent unless it has a distinct repeatable lifecycle,
owner boundary, stop-lines, and focused validation of its own.

The topology manifest is the authoritative inventory of active packages and
parts. Documentation may explain that inventory but must not invent additional
active routes.

## Design principles

1. **Owner evidence before projection.** No read model outranks its source.
2. **Source meaning before operation convenience.** Mechanics serve stats
   contracts; they do not swallow them.
3. **One active home per payload.** Compatibility is explicit, not duplicated
   canon.
4. **Shared parent, local part.** Reuse AoA mechanic language where the
   lifecycle is genuinely shared.
5. **Cross-routed growth.** Every active stats family can find its mechanic,
   and every mechanic part can find the stats family it serves.
6. **Determinism and visible freshness.** The same registered evidence yields
   the same projection, with staleness and absence preserved.
7. **Thin access planes.** CLI, systemd, and MCP surfaces call bounded core
   behavior without becoming owner truth.

## Good shape

- a source family names its semantics and authority ceiling
- its manifest entry points to implementation, output, and mechanic routes
- a mechanic part owns one coherent repeatable operation
- root entrypoints are either canonical by declaration or thin compatibility
  surfaces
- validators check the crosswalk in both directions

## Bad shape

- creating every sibling mechanic package only for visual symmetry
- treating every stats summary name as a new top-level mechanic
- moving source schemas or authored meaning under mechanics because a builder
  uses them
- keeping two active copies of a payload during migration
- allowing generated counts to make claims the owner evidence does not support

## Relationship to root guidance

`AGENTS.md` is the operating route card. This document defines the durable
shape and tradeoffs behind that route. Nested route cards narrow the law for a
source family, mechanic package, part, implementation, or compatibility
district.

`ROADMAP.md` decides sequencing and remaining work. `docs/decisions/` records
durable choices only when the rationale cannot be recovered adequately from
the design and topology surfaces themselves.

## Use by agents

Before changing structure, identify:

1. the source-owned fact being observed
2. the `stats/` family that owns the derived meaning
3. the shared mechanic parent and local part that own the operation
4. the current canonical payload and any compatibility consumers
5. the focused validator that proves the cross-contract

If one of these is unknown, make the route explicit before moving payloads.
