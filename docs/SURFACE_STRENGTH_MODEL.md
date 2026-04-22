# Surface Strength Model

## Purpose

`aoa-stats` needs more than a list of surfaces.
It needs an explicit way to say how strong each surface is, what it depends on,
and what it must never overrule.

That is what the catalog now carries.

## Per-surface fields

Each catalog entry keeps:

- `input_posture`: what kind of evidence chain the surface reads
- `owner_truth_inputs`: which owner surfaces remain stronger
- `authority_ceiling`: the sentence that states where this summary stops
- `consumer_risk`: how dangerous a misread would be
- `live_state_capable`: whether the surface can participate in the local live
  refresh loop

Together these fields form the stats-owned surface profile that consumers may
use as a re-grounding signal. The profile names caution and stronger owner
inputs; it does not decide whether a route, proof, workflow, or quest state is
true.

## Input posture classes

Use these classes as the compact posture vocabulary:

- `receipt_backed_live`: active receipts are the direct source
- `receipt_backed_with_external_reports`: receipts plus linked report artifacts
- `checked_in_owner_history`: checked-in source-owned history or runtime entry
  surfaces
- `reviewed_example_chain`: reviewed examples and anchor artifacts
- `registry_backed_coverage_audit`: receipt counts checked against the live
  source registry

This is a small vocabulary on purpose.

## Consumer risk

- `low`: convenient counts with limited authority drift risk
- `medium`: easy to overread if the user forgets the owner split
- `high`: should regularly send the reader back to owner-local proof, route, or
  runtime surfaces

## Deferred contract-only surfaces

Not every schema or doctrine should become a live generated summary just
because it exists.

If a family is still waiting for an honest input chain, keep it in
`deferred_contract_surfaces` with:

- `status=contract_only`
- the contract refs
- an activation condition
- an explicit authority ceiling

Today `antifragility_vector` stays in that deferred posture.

## Boundary rule

Surface strength metadata helps `aoa-stats` become a better participant in the
federation.
It does not make `aoa-stats` sovereign.

For the consumer-facing re-grounding contract, read
`CONSUMER_REGROUNDING_SIGNALS.md`.
