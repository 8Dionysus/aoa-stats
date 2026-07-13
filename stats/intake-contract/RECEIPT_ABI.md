# Receipt ABI Governance

## Purpose

`aoa-stats` owns the shared receipt envelope for cross-repo derivation, so it
also owns the admission law that keeps this seam stable.

That law stays narrow:

- one canonical envelope at `schemas/stats-event-envelope.schema.json`
- one active event-kind registry at `stats/intake-contract/event-kind-registry.json`
- mirrored copies in downstream repos only when they clearly point back to the
  canonical schema

## What this governs

This surface governs:

- which `event_kind` values are active
- which repo currently owns the payload contract for each event family
- which summary families consume that event family today
- how mirror copies stay subordinate to the canonical schema

It does not transfer payload ownership away from the owner repos named in the
registry.

## Registry law

`stats/intake-contract/event-kind-registry.json` is the admission table for active
cross-repo event kinds.

Each entry must keep:

- `event_kind`
- `status`
- `payload_owner_repo`
- `summary_surface_names`

The active entries must match the enum order in
`schemas/stats-event-envelope.schema.json` exactly.

That keeps the shared envelope machine-friendly while still letting the stats
layer explain which compatibility families remain admissible.

Registry `status=active` means the compatibility envelope may admit the event
kind. It does not prove that a current owner publishes it or that the live
source registry observes it. Runtime-wave closeout is intentionally
envelope-admissible for the committed historical fixture while absent from the
current live-source registry.

## Feed resolution law

The crossing operation may load bounded JSON and JSONL feeds, validate their
envelopes, and deduplicate equal `event_id` values by the latest
`(observed_at, event_id)` observation. It may also resolve an explicit valid
`supersedes` family to its latest descendant before projection.

That normalization is deliberately conservative. A missing supersedes target
or a cycle remains visible in the active set; intake must not erase ambiguous
evidence merely to produce a cleaner count. Resolution does not mutate source
receipts and does not claim that a newer observation has stronger owner truth.

## Mirror law

When a sibling repo keeps a local mirror of the shared envelope schema, that
copy may change only in identity metadata such as `$id`, title, description,
or an explicit canonical back-reference.

The structural contract must stay identical.

Today `aoa-evals/schemas/stats-event-envelope.schema.json` is the required
mirror check.

## Admission rule for a new event family

Add a new cross-repo event family only when all of the following are true:

1. one owner repo is clearly responsible for the payload contract
2. at least one stats surface has a bounded question that actually needs the
   event
3. the event does not collapse proof, workflow, routing, or quest meaning into
   one generic telemetry bucket
4. the new family can be validated without silent inference from raw log volume

If any of those conditions are weak, do not widen the envelope yet.

## Deprecation rule

Deprecated event kinds stay in the registry with `status=deprecated` until the
canonical envelope and every live publisher have stopped emitting them.

The shared schema enum only carries active kinds.

## Verification

Use [`AGENTS.md#verify`](AGENTS.md#verify) and the receipt crossing's
[`VALIDATION.md`](../../mechanics/boundary-bridge/parts/receipt-abi-crossing/VALIDATION.md).

Those checks cover:

- canonical schema structure
- active registry parity with the canonical enum
- mirror parity against `aoa-evals` when the sibling repo is present
- JSON/JSONL loading, latest-event deduplication, and conservative supersedes
  resolution
