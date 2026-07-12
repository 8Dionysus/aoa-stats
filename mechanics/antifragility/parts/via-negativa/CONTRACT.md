# Via-negativa stats review contract

## Input

Current or proposed derived stats surfaces, their named consumers, evidence
posture, and suppression behavior.

## Operation

`docs/VIA_NEGATIVA_CHECKLIST.md` guides a human review of whether a weak view
should be kept, merged, moved, suppressed, quarantined, deprecated, or deleted.
Every candidate route names the owner and the provenance that survives. It does
not execute any of those actions.

## Boundary

The checklist cannot make a deletion decision, infer lack of value from lack
of volume, replace owner evidence, or turn a preferred vector into proof,
rank, routing, gate, identity, or workflow truth.

Source evidence that must be retained is not a subtraction candidate. A move
or deletion stops until the owner repository reviews it. Proof failure routes
first to `aoa-evals`, not through observability cleanup.

## Crosswalk

The authored stats question and authority ceiling live at
`stats/operation-contracts/active/antifragility.via-negativa.operation.json`;
the reciprocal route and part-local test district are enforced by
`mechanics/topology.json` and `stats/source_home.manifest.json`.
