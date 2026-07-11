# ANTIFRAGILITY VECTOR

## What this surface is

`aoa-stats` may derive antifragility vectors from source-owned receipts and bounded eval reports.

This is a **derived view**, not a new owner of meaning.

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

## Wave 1 note

Wave 1 is intentionally small. It is enough to define one schema, one example,
and the doctrine that keeps the layer out of score-empire drift.

For now this family stays contract-only in the summary catalog.
It does not become a generated live summary until one owner-linked repeated
stress family and one bounded eval chain exist for the same stressor family.
