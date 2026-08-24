# AOST-D-0021 Current-Main Validation Telemetry Convergence

## Index Metadata

- Decision ID: AOST-D-0021
- Original date: 2026-08-24
- Surface classes: stats/measurement-contract, stats/federation, schemas/validation, src/core, scripts/validators, tests, docs/decisions
- Stats surfaces: validation telemetry packet, validation telemetry port, coverage baseline
- Source lanes: owner-local validator manifests, owner validation receipts, aoa-stats source inventory
- Guard families: derived-only authority, source coverage, identity binding, missingness, schema admission, batch-local replay, current-main compatibility
- Posture: candidate; independent review required

## Context

origin/main@88ff38b1b38eef939f2c5b4541cbe8363a05fc8d already carries the
accepted owner-safe validation telemetry baseline from AOST-D-0019. The reviewed
historical convergence line adds stricter nested packet admission, owner-source
and port binding, timing and cost posture, identity grouping, and explicit
batch-local duplicate protection. Its old five-path landing candidate cannot be
replayed mechanically onto current main because current main carries a divergent
telemetry implementation and schema shape.

The bounded consumer needs those guards to keep expected, rejected, missing,
stale, incompatible, identity, replay, and schema-collision cases visible
without turning telemetry into proof, validator sufficiency, runtime health,
live currentness, or owner acceptance.

## Decision

Extend the existing aoa-stats validation telemetry compatibility surface on
current main through one owner-consistent source/schema/validator/test route.
Require callers to pass canonical JSON-Schema findings into the pure admission
boundary, bind admitted packets to an explicit owner port and exactly one
declared lane/export, and preserve complete candidate/environment/source
identity, timing/cost references, and explicit missingness states.

Project only compatible identity groups. Block incompatible candidate,
environment, port, source, revision, or live/reference groups instead of
pooling them. Reject same-batch duplicate observations while documenting that
historical reseal prevention remains outside aoa-stats. Keep generated and
committed examples on the reference route and rebuild them from current owner
inputs.

## Options Considered

- Sequentially replay the five historical commits and resolve conflicts as they appear.
- Keep the current-main subset and omit the richer admission and identity cases.
- Reconstruct the complete route from current-main owner meaning and the reviewed richer boundary, then validate it independently.

## Rationale

Mechanical replay stops at current-main implementation and schema collisions,
so it cannot establish which current owner contracts remain authoritative. The
subset route passes basic shape checks but loses nested-schema closure, owner
identity, lane/export binding, and explicit replay ceilings. Semantic
reconstruction preserves current-main release and external-owner snapshot
behavior while restoring only the telemetry guards required by the bounded
question and its negative cases.

The result remains a derived compatibility/read-model surface. A packet digest
or admission receipt is not a source signature; identity compatibility is not
causal attribution; counts and timing are not proof; and reference/generated
inputs are not live observations.

## Consequences

The owner port and packet schemas now expose timing, cost, lane evidence, and
acceptance-barrier references explicitly. The pure builder rejects raw packet
mappings, preserves missing/unknown/stale states, and records identity barriers
without aggregating incompatible groups. The repository needs focused negative
tests and generated/index validation before a candidate can enter independent
review.

No durable replay ledger, source-owner authentication, proof verdict, runtime
observation, deployment, GitHub landing, Goal acceptance, owner acceptance, or
human acceptance is created by this decision.

## Source Surfaces

- stats/measurement-contract/README.md
- stats/measurement-contract/validation-telemetry-packet.schema.json
- stats/federation/README.md
- stats/federation/validation-telemetry-port.schema.json
- schemas/validation-telemetry-baseline.schema.json
- src/aoa_stats_builder/validation_telemetry.py
- scripts/build_validation_telemetry_baseline.py
- scripts/validate_stats_protocol.py
- tests/test_validation_telemetry.py
- AOST-D-0019-owner-safe-validation-telemetry.md

## Validation

The candidate must pass the focused telemetry negative-first suite, generated
fixed-point and projection checks, stats protocol/source-home/mechanics
validators, nested-agent and decision-record checks, repository tests, and the
release gate. This note is rationale only; it does not turn any green command
into landing, runtime, proof, Goal, owner, or human acceptance.
