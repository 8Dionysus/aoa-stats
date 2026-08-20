# AOST-D-0018 Memory Outcomes Remain Measurement, Not Authority

## Index Metadata

- Decision ID: AOST-D-0018
- Original date: 2026-07-29
- Surface classes: stats/measurement-contract, stats/federation, mechanics/boundary-bridge
- Stats surfaces: outcome receipt, episodic utility aggregate, agent-local federation aggregate
- Source lanes: aoa-memo memory packets, aoa-evals verdicts, abyss-stack delivery receipts, abyss-machine host evidence
- Guard families: derived-only authority, source coverage, no policy promotion, no access-count utility
- Posture: accepted

## Context

R1 needs outcome, action-change, delayed-harm, resource, and operator-cost
measurement without turning a convenient aggregate into memory truth or a
self-applying policy.

## Decision

`aoa-stats` owns the compatible C10 outcome-receipt grammar and descriptive
cross-owner aggregates. Source owners retain task, memory, delivery, host, and
operator facts; `aoa-evals` retains proof verdicts.

Access count is never utility. Missing attribution, unresolved delayed
outcomes, reward-hacking failure, accidental success, unavailable evals, or
unknown memory use cannot strengthen policy. Stats output may support a
proposal, never semantic promotion, deletion, tenant expansion, permission,
training, or self-approval.

## Options Considered

- Let a positive aggregate automatically tune memory.
- Let `aoa-evals` own the shared measurement ABI.
- Keep outcomes untyped and compare prose.
- Use a source-linked stats contract with explicit authority ceilings.

## Rationale

The typed derived route makes cost and result comparable without moving
meaning or verdict authority into the aggregation layer.

## Consequences

- R1 can measure operator minutes, host cost, task result, delayed harm, and
  rollback against exact receipts.
- Policy learning remains frozen until a separate owner/operator gate.
- Generated stats readers remain weaker than source receipts.

## Source Surfaces

- `stats/measurement-contract/outcome-receipt.schema.json`
- `src/aoa_stats_builder/outcome.py`
- `mechanics/boundary-bridge/parts/measurement-packet-crossing/`
- `docs/BOUNDARIES.md`
- `docs/ARCHITECTURE.md`

## Validation

Use the decision-index, receipt-schema, boundary-bridge, nested-agent,
repository, and full test routes named by the owning cards.
