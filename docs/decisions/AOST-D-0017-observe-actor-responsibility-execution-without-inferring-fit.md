# Observe Actor Responsibility Execution Without Inferring Fit

## Index Metadata

- Decision ID: AOST-D-0017
- Original date: 2026-08-12
- Surface classes: stats/intake-contract, schema/receipt-abi, owner evidence, validation boundary
- Stats surfaces: Object, Repeated Window, Source Coverage
- Source lanes: aoa-agents summon-result-v4, aoa-sdk incarnation binding, abyss-stack external actor runtime and A2A return
- Guard families: owner-contract compatibility, derived-only authority, no acceptance inference, no proof inference, mirror parity
- Posture: accepted

## Context

Role-first external actors now preserve one evidence-complete execution result
through `aoa-agents` `summon-result-v4`, with exact owner-qualified references
to the selected role and incarnation, runtime result, A2A return, usage
observation, effects, review, outcome, and acceptance posture.

The existing runtime wave, trial, and return receipt families describe other
owner contracts and are not aliases for an actor holding and returning a
bounded responsibility. Reusing one of them would erase the distinction
between runtime transport, A2A responsibility, and the role-bearing execution
that `aoa-agents` owns. At the same time, absorbing the owner payload into
`aoa-stats` would let a derived observability layer redefine model fit,
benefit, or owner acceptance.

The canonical stats envelope also has a subordinate validation mirror in
`aoa-evals`. Its current location is under the publication-receipts mechanic;
continuing to validate the removed root-level path would make cross-owner ABI
drift invisible.

## Decision

Admit `actor_responsibility_execution_receipt` as a distinct stats event kind.
Its payload owner is `aoa-agents`, and its stronger meaning remains the
owner-valid `summon-result-v4` evidence chain. `aoa-stats` may project the
receipt only through the generic Object, Repeated Window, and Source Coverage
surfaces; this admission does not activate a live source or create a dedicated
benefit, model-fit, performance, or acceptance surface.

Receipt presence proves only that one owner-qualified actor responsibility
execution or closeout observation was published. Runtime success, returned
artifacts, reviewer disposition, owner acceptance, and model fit remain
separate explicit fields or referenced owner evidence and may remain unknown.
The canonical validator follows the current `aoa-evals` publication-receipts
mirror path and fails when that subordinate schema drifts.

## Options Considered

- Reuse a runtime wave, trial, or return event kind: rejected because those
  owner contracts do not carry the same role and responsibility meaning.
- Create a stats-owned actor execution payload: rejected because `aoa-stats`
  must not absorb `aoa-agents`, runtime, A2A, review, or acceptance authority.
- Admit a distinct owner-qualified event kind with only generic summaries:
  chosen because it makes real executions countable while preserving every
  stronger owner boundary.
- Activate a live publisher and dedicated actor-performance surface now:
  rejected until a reviewed producer, observation window, and explicit
  measurement contract exist.

## Rationale

A separate event family keeps actor responsibility visible without flattening
it into process launch or model invocation. Pointing to the exact owner result
also lets later work examine cost, recurrence, effects, and returns without
turning derived counts into a verdict about the actor or incarnation.

Restoring validation against the current evals mirror closes an existing
governance blind spot at the same boundary where the canonical enum grows.

## Consequences

- Producers must publish an `aoa-agents`-owned payload whose references retain
  the exact runtime, A2A, usage, effect, review, outcome, and acceptance
  evidence rather than copying or renaming it.
- Generic stats summaries can count and group admitted observations, but may
  not infer benefit, model suitability, task success, review approval, or
  owner acceptance.
- Absence from a receipt feed means unobserved, not zero executions.
- Event-kind admission alone does not register a live source, install a
  watcher, or establish a recurring measurement window.
- Any future dedicated actor or model surface requires its own source-owner
  agreement, real publisher evidence, strength classification, and validation.
- Canonical stats and the subordinate evals mirror must land and remain in
  exact normalized parity.

## Source Surfaces

- `schemas/stats-event-envelope.schema.json`
- `stats/intake-contract/event-kind-registry.json`
- `stats/intake-contract/RECEIPT_ABI.md`
- `src/aoa_stats_builder/receipt_abi.py`
- `mechanics/boundary-bridge/parts/receipt-abi-crossing/tests/test_receipt_abi_governance.py`
- `mechanics/boundary-bridge/parts/receipt-abi-crossing/tests/test_receipt_feed_resolution.py`
- `aoa-agents:skills/aoa-summon/references/summon-result-v4.schema.json`
- `aoa-agents:docs/decisions/AOA-AG-D-0063-evidence-complete-summon-v4.md`
- `aoa-evals:mechanics/publication-receipts/parts/stats-envelope-mirror/schemas/stats-event-envelope.schema.json`

## Validation

Run the decision-lane checks in [`AGENTS.md#verify`](AGENTS.md#verify), the
receipt ABI validator and focused crossing tests, source-home and protocol
validators, and normalized canonical-to-mirror comparison. The repository
release gate remains the final source proof; live-source activation requires a
separate end-to-end producer and observation proof.
