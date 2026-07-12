# ANTIFRAGILITY VECTOR

## What this surface is

`aoa-stats` may eventually derive antifragility vectors from source-owned
receipts and bounded eval reports.

This is a **derived view**, not a new owner of meaning.

The current surface is contract-only. It has no builder or published vector.

## Why a vector

A single total score would blur distinct questions such as:

- was the event contained
- was the fallback truthful
- did operator burden rise or fall
- did later adaptation actually improve handling

Split axes keep the layer legible and reduce authority drift.

## Suggested axes

- `containment`
- `reversibility`
- `fallback_fidelity`
- `recovery_latency`
- `evidence_density`
- `adaptation_gain`
- `operator_burden`
- `trust_calibration`

For the stats layer, higher numbers should mean healthier posture. If an underlying source metric points in the opposite direction, normalize it before publication.

## Input discipline

The vector should be built from:

- source-owned stressor receipts
- source-owned adaptation deltas when present
- bounded eval reports

The vector should not be inferred from raw log volume alone.

The current grounded chain is intentionally asymmetric:

- ATM10-Agent `scripts/hybrid_query_demo.py` emits
  `stressor_receipt_v1` for one bounded retrieval-only fallback;
- ATM10-Agent `adaptation_delta_v1` is schema/example only and is not emitted
  by that runtime;
- `aoa-evals/evals/stress/aoa-antifragility-posture/` is a draft
  docs/example bundle, not an executed current proof chain;
- no repeated owner/eval window demonstrates improvement for the same stressor
  family.

## Output posture

The vector should publish:

- scope
- input references
- sample size
- suppression state when evidence is too thin
- split numeric axes

The vector should not publish:
- new workflow meaning
- proof narratives that belong in `aoa-evals`
- central source-of-truth claims about local owner surfaces

## Suppression guidance

When evidence is too thin, prefer:
- `suppression.status=low_sample`
- null values for uncertain axes
- an explicit reason

A weak but honest vector is healthier than a confident fiction.

The checked-in example therefore uses
`suppression.status=insufficient_evidence`, an empty
`adaptation_delta_refs` list, and null values for every axis. It demonstrates
the schema boundary; it is not a current ATM10-Agent measurement.

## Activation gate

All four gaps in
`stats/read-models/deferred/antifragility_vector.profile.json` must close for
the same stressor family:

1. register and validate the owner runtime receipt route for stats intake;
2. emit source-owned adaptation deltas at runtime;
3. execute the bounded eval over current owner receipts and reports;
4. establish a repeated owner/eval window that can support movement claims.

Activation is a separate reviewed change. It must introduce the producer,
active profile and new slot, generated/public output contract, validation,
consumer review, and any honest live observation route together. Catalog
visibility of this deferred contract is not activation and does not authorize
MCP promotion.
