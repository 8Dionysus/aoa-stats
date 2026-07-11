# Titan memory-owner bridge contract

## Input

Titan/session receipts and eval outputs remain owned by `aoa-sdk`, their
runtime owners, and the relevant proof surfaces. Durable memory truth remains
owned by `aoa-memo`.

## Operation

The part documents receipt-derived session, gate, closeout, recall, redaction,
candidate-ratio, and owner-distribution metrics. Its local schema constrains a
candidate metrics object; no builder or live feed is claimed.

## Boundary

Counts cannot confirm memory, define a Titan role, open a gate, establish seed
canon, or become proof, routing, identity, runtime, or workflow truth.

## Crosswalk

The authored stats question and authority ceiling live at
`stats/operation-contracts/active/titan.memory-owner-bridge.operation.json`;
the reciprocal route is enforced by `mechanics/topology.json`.
