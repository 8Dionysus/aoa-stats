# Titan runtime-console stats contract

## Input

`aoa-sdk` Titan receipts and their runtime/session owners retain the truth of
session opens, closes, approvals, Forge/Delta gates, violations, and failures.

## Operation

The part documents candidate console and runtime metric families over those
receipts. It has no local schema, builder, live feed, or current runtime-state
claim.

## Boundary

Metrics cannot open or close a session, grant approval, activate Forge or
Delta, mutate a receipt, diagnose a live runtime, or become proof, routing,
gate, identity, or workflow truth.

## Crosswalk

The authored stats question and authority ceiling live at
`stats/operation-contracts/active/titan.runtime-console.operation.json`; the
reciprocal route is enforced by `mechanics/topology.json`.
