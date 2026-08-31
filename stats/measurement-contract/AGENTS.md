# AGENTS.md

Route card for the shared measurement contract.

## Scope

This family owns the portable statistical grammar used to describe an
owner-local measurement, one evidence-linked packet, and one content-minimized
action/outcome observation. It owns compatibility rules for those shapes, not
the meaning of an owner's metric, task result, or verdict.

## Conditional route

When a measurement question is known, follow the family README and selected
source schemas, then the reciprocal Boundary Bridge measurement-packet
crossing route named by `stats/source_home.manifest.json`. Open only the pure
implementation or packet-read route required by the question.

## Owner law

- A measurement identity has one writer owner.
- Population, sample, window, unit, dimensions, missingness, uncertainty,
  provenance, reporting rule, privacy, and live posture remain explicit.
- `missing`, `unknown`, and `stale` never become zero, failure, or success.
- A ratio preserves numerator and denominator; a distribution preserves its
  represented sample size.
- A derived packet stays weaker than owner evidence and any eval verdict it
  carries.
- Outcome receipts record action snapshots, terminal and delayed observations,
  costs, harm, confounders, accidental success, and attribution uncertainty
  without asserting causality.
- Unknown memory use or missing action snapshots remain unknown and cannot be
  relabelled as success or admitted for training.
- The shared schemas define shape only. Owner-local questions and definitions
  belong in the owner's root `stats/` port.

## Stop lines and validation

Do not place owner payloads, generated views, runtime state, raw traces, raw
session material, or MCP implementation here. Do not add a global quality
score, causal verdict, policy-training grant, or write/action contract. Focused
semantic proof belongs to the reciprocal part; root validation and the complete
gate remain on-demand in `VALIDATION.md` and `scripts/release_check.py`.
