# Architecture

## One sentence

`aoa-stats` is an evidence-linked observability layer that turns bounded,
owner-local facts into deterministic read models without promoting those
models into owner truth.

## Authority ladder

The layer is deliberately downstream:

1. owner repositories define payload meaning and current domain facts
2. bounded proof owners define verdict meaning
3. stats-authored profiles and operation contracts define derived questions
4. builders project those contracts into public read models
5. catalogs, MCP, KAG, bundles, and consumer caches expose weaker views

No lower step may silently strengthen, repair, or replace an upper one.

## Five layers

### 1. Event facts

Append-only receipts say what happened. The shared envelope lives at
`schemas/stats-event-envelope.schema.json`; admission meaning and the active
event vocabulary live under `stats/intake-contract/`. Owner repositories still
own the payload contracts carried inside the envelope.

Corrections remain append-only. A resolvable `supersedes` link may collapse an
older event in an active projection, but the raw feed retains both facts.

### 2. Evidence links

Receipts point to inspectable artifacts through `evidence_refs`. Stats should
not copy raw patches, logs, reports, or owner state merely to make a summary
self-contained.

### 3. Bounded evaluations

Quality enters through bounded verdicts and review surfaces. `aoa-stats` may
quote or aggregate their declared results, but it does not reinterpret proof
or make a draft/example verdict current.

### 4. Progression readings

Progression remains route-scoped or quest-scoped and multi-axis. Deltas,
cautions, holds, advances, reanchors, and downgrades do not become one
sovereign score.

### 5. Derived read models

Read models answer bounded questions with deterministic rules. Authored
profiles under `stats/read-models/` define each public surface's meaning,
inputs, authority ceiling, lifecycle, and live-admission posture. Non-catalog
questions use records under `stats/operation-contracts/`.

Exact current counts, named active/reference/retired rosters, and individual
surface rationale belong to those authored records, the generated catalog,
and indexed decisions. They are not maintained in this architecture document.

## Source and operation split

`stats/` owns source-authored meaning. `mechanics/` owns repeatable intake,
projection, refresh, validation, and publication operations around that
meaning. `stats/source_home.manifest.json` and `mechanics/topology.json` are the
reciprocal machine-readable crosswalks.

An operation-specific document, fixture, validator, or focused test belongs to
the nearest mechanic part. Stable public schemas and generated outputs retain
their root paths, but their meaning routes back to authored stats sources.

## Projection boundary

Filesystem-free transformation rules belong in `src/aoa_stats_builder/`.
Source discovery, filesystem loading, write/check mode, CLI policy, and output
fan-out stay at adapters and entrypoints. A shared implementation core does not
move operation-specific proof away from its mechanic owner.

Generated views remain machine-first and reproducible. Missing, stale,
rejected, or unregistered evidence stays visible; it is never converted into
success, current state, or an invented zero.

## Catalog and lifecycle

`generated/summary_surface_catalog.min.json` is the compact public discovery
surface. It is projected from authored profiles and validated by
`schemas/summary-surface-catalog.schema.json`; it is not an edit source.

The stable catalog vocabulary covers identity, derivation, input posture,
stronger owner inputs, authority ceiling, consumer risk, validation, and live
capability. `stats/surface-catalog/SURFACE_STRENGTH_MODEL.md` explains that
vocabulary.

Lifecycle is intentionally asymmetric:

- active profiles author public surfaces
- deferred profiles expose evidence-gated contract candidates without output
- retired profiles retain cleanup and provenance posture without publication

Local live materialization admits only active profiles whose authored contract
allows it and whose source can be observed moving. It publishes only outputs
actually materialized and does not fall back to committed examples or retired
defaults when live input is missing.

## Publication and access

`artifact_identity` describes the public catalog's ABI and provenance posture;
it is not a release signature. The OS Abyss artifact-bundle validator adds ABI,
subject-inventory, registry, and isolated materialization checks without
making the catalog stronger than its source evidence.

The read-only access plane under `src/aoa_stats_mcp/` may expose the catalog,
surface payloads, and this boundary text. Access convenience does not alter
authority, activate a profile, or turn committed reference data into live
state.

## Canonical questions

- counts answer how often and how widely
- bounded verdicts answer how well on one declared surface
- progression answers what changed on named axes
- evidence refs answer where to inspect next
- source coverage answers which registered owners are represented

None of these alone proves mastery, intent, causality, self-agency, workflow
state, or owner health.

## Read next

- authority stop-lines: `docs/BOUNDARIES.md`
- source families and exact lifecycle state: `stats/README.md`
- operation ownership: `mechanics/README.md`
- consumer caution vocabulary: `stats/surface-catalog/SURFACE_STRENGTH_MODEL.md`
- durable rationale: `docs/decisions/README.md`
