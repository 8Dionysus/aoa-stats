# Surface Strength Model

## Purpose

`aoa-stats` needs more than a list of surfaces. It needs an explicit way to
say how strong each surface is, what it depends on, and what it must never
overrule.

That is what the catalog carries.

## Ownership and vocabulary law

This source family owns the shared human vocabulary behind authored active and
deferred surface profiles. Every `input_posture` used by those profiles must
match one class below, and catalog validation checks that exact set in both
directions.

Add a class here before an authored profile uses it. Remove a class when no
active or deferred profile uses it. Exact surface lifecycle, owner inputs, and
activation gaps belong to the target profile and indexed decisions rather than
this shared model.

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

- `receipt_backed_live`: active receipts are the direct source
- `checked_in_owner_history`: checked-in source-owned history or runtime entry
  surfaces
- `reviewed_example_chain`: reviewed examples and anchor artifacts
- `committed_owner_example_chain`: a coherent set of checked-in examples from
  one owner repository that supports a deterministic committed reference
  snapshot without claiming deploy-local or runtime occurrence
- `committed_cross_owner_example_chain`: checked-in examples from multiple
  stronger owners agree on one deterministic reference shape without proving
  current owner state or runtime occurrence
- `committed_reference_example_catalog_chain`: committed examples, an
  owner-authored contract, and catalog definitions that make a reference shape
  inspectable without claiming runtime occurrence
- `committed_legacy_numeric_receipt_snapshot`: a stable numeric receipt
  projection retained for compatibility when the current owner contract is
  semantic and no authorized score mapping exists
- `reviewed_owner_corpus_snapshot`: a committed projection of authentic
  reviewed owner corpus truth that is not continuously live without an
  observable refresh route
- `committed_draft_eval_example_chain`: a committed eval receipt/report example
  whose draft posture cannot stand in for an activated producer or current
  proof family
- `registry_backed_coverage_audit`: receipt counts checked against the live
  source registry
- `partial_owner_runtime_draft_eval_chain`: one current owner runtime publisher
  exists, but companion adaptation, eval execution, intake registration, or
  repeated-window evidence remains incomplete

This is a small, closed vocabulary on purpose.

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
- the current `input_posture`
- exact `owner_truth_inputs` for the real part of the chain
- an activation condition
- non-empty, unique `activation_gaps`
- an explicit authority ceiling
- a `consumer_risk` rating

Read the target deferred profile and its indexed decision for exact current
posture. Visibility of those facts is caution metadata, not activation.

## Boundary rule

Surface-strength metadata helps `aoa-stats` become a better participant in the
federation. It does not make `aoa-stats` sovereign.

For the consumer-facing re-grounding contract, read
`CONSUMER_REGROUNDING.md`.
