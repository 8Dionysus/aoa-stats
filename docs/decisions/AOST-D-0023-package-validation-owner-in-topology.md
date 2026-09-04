# AOST-D-0023 Package Validation Owner In Topology

## Index Metadata

- Decision ID: AOST-D-0023
- Original date: 2026-09-04
- Surface classes: validation, mechanics topology, docs route, public contract
- Stats surfaces: mechanics package, owner-local validation, growth-cycle projections
- Source lanes: mechanics topology, owner-local validators
- Guard families: owner authority, source coverage, validation completeness
- Posture: accepted explicit package validation owner; part ownership remains the default

## Context

Focused validation normally belongs to the nearest mechanic part. Audit and
Growth Cycle are the evidenced exceptions: each has multiple parts using one
importable deterministic core and one cross-part projection suite under the
mechanic package. Copying either invocation into every part route would create
multiple human owners; leaving the package `VALIDATION.md` outside topology
would create an unregistered procedure surface.

## Decision

A mechanic package may own one exact cross-part procedure only when it protects
one genuinely shared core and its test district is already declared by
`package_payload_roots`. The topology must additionally name the exact package
`VALIDATION.md` through `package_validation_surface`. Part validation routes
link to that owner instead of copying its invocation.

Part-local ownership remains the default. The topology validator rejects an
undeclared package validation file, a missing declared owner, or a field that
points outside its package. Root validation owns only wider repository checks
and links to the package or part owner after the affected operation is known.

## Options Considered

- Copy the shared suite into every affected part validation route.
- Assign the shared procedure arbitrarily to one part.
- Treat every package as an implicit validation owner.
- Admit the evidenced exception through one explicit topology field.

## Rationale

The explicit field preserves one human owner without weakening the placement
law or making every package an implicit validation owner. It keeps each
exception discoverable from the same machine-readable topology that owns
operation placement and lets the validator distinguish a deliberate shared
route from documentation residue.

## Consequences

- Audit and Growth Cycle each have one declared owner for their shared
  projection suite.
- Part routes remain small and retain ownership of genuinely local procedures.
- A new package-level procedure requires shared-core evidence, a payload-root
  declaration, an exact validation-surface declaration, and validator coverage.
- The declaration does not make focused green evidence into repository,
  release, runtime, owner-acceptance, or proof-sufficiency evidence.

## Source Surfaces

- `mechanics/topology.json`
- `mechanics/audit/VALIDATION.md`
- `mechanics/audit/parts/*/VALIDATION.md`
- `mechanics/growth-cycle/VALIDATION.md`
- `mechanics/growth-cycle/parts/*/VALIDATION.md`
- `scripts/validate_mechanics_topology.py`
- `tests/test_mechanics_topology.py`
- `AGENTS.md`
- `DESIGN.md`
- `README.md`
- `VALIDATION.md`

## Validation

Use the decision-index checks and the mechanics topology validator through
[`../../VALIDATION.md`](../../VALIDATION.md), then run the declared Growth Cycle
[package validation route](../../mechanics/growth-cycle/VALIDATION.md). These
checks establish route integrity and focused behavior only.
