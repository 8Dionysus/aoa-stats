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
- `committed_owner_example_chain`: a coherent set of checked-in examples from
  one owner repository that supports a deterministic committed reference
  snapshot without claiming deploy-local or runtime occurrence
- `committed_reference_example_catalog_chain`: committed examples, an
  owner-authored contract, and catalog definitions that make a reference shape
  inspectable without claiming runtime occurrence
- `committed_receipt_example_chain`: committed receipt examples whose event
  family is inspectable but has no active owner publisher
- `committed_historical_wave_receipt_snapshot`: a stable historical wave-receipt
  projection retained for compatibility when current owner trial or return
  receipt contracts differ and are not authorized aliases
- `reviewed_owner_corpus_snapshot`: a committed projection of authentic
  reviewed owner corpus truth that is not continuously live without an
  observable refresh route
- `committed_draft_eval_example_chain`: a committed eval receipt/report example
  whose draft posture cannot stand in for an activated producer or current
  proof family
- `registry_backed_coverage_audit`: receipt counts checked against the live
  source registry
- `partial_owner_runtime_draft_eval_chain`: one current owner runtime
  publisher exists, but companion adaptation, eval execution, intake
  registration, or repeated-window evidence remains incomplete

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
- the current `input_posture`
- exact `owner_truth_inputs` for the real part of the chain
- an activation condition
- non-empty, unique `activation_gaps`
- an explicit authority ceiling
- a `consumer_risk` rating

Today `antifragility_vector` stays in that deferred posture. Its ATM10-Agent
stressor publisher is real, but adaptation emission, stats intake
registration, executed eval evidence, and a repeated same-family window are
not. Publicly naming those facts is caution metadata, not activation.

## Boundary rule

Surface strength metadata helps `aoa-stats` become a better participant in the
federation.
It does not make `aoa-stats` sovereign.

For the consumer-facing re-grounding contract, read
`../stats/surface-catalog/CONSUMER_REGROUNDING.md`.
