# AGENTS.md

Route card for the shared measurement contract.

## Scope

This branch owns the portable statistical grammar used to describe an
owner-local measurement and one evidence-linked measurement packet. It owns
compatibility rules for those shapes, not the meaning of any owner's metric.

Read `README.md`, then the two source schemas. For executable behavior, follow
the reciprocal Boundary Bridge part named by `stats/source_home.manifest.json`.

## Owner law

- A measurement identity has one writer owner.
- Population, sample, window, unit, dimensions, missingness, uncertainty,
  provenance, reporting rule, privacy, and live posture remain explicit.
- `missing`, `unknown`, and `stale` never become zero, failure, or success.
- A ratio preserves numerator and denominator. A distribution preserves its
  represented sample size.
- A derived packet stays weaker than its owner evidence and any eval verdict it
  carries.
- The schemas define shared shape only. Owner-local questions and definitions
  belong in the owner's root `stats/` port.

## Stop lines

Do not place owner payloads, generated views, runtime state, raw traces, raw
session material, or MCP implementation here. Do not add a global quality
score or a write/action contract.

## Verification

The executable owner is `scripts/release_check.py`; focused semantic proof is
owned by the reciprocal measurement-packet crossing part.
