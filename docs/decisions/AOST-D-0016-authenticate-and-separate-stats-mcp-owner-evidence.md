# Authenticate And Separate Stats MCP Owner Evidence

## Index Metadata

- Decision ID: AOST-D-0016
- Original date: 2026-08-01
- Surface classes: stats/surface-catalog, MCP/access, owner evidence, security boundary
- Stats surfaces: summary surface catalog, source identity, grounding review, freshness projection
- Source lanes: aoa-stats, aoa-sdk, abyss-stack, aoa-evals
- Guard families: authenticated issuer, derived-only authority, exact source identity, no acceptance inference, no proof inference
- Posture: accepted

## Context

`AOST-D-0015` separated stack capture from stats-owner interpretation, but its
first implementation accepted the v1 content-addressed capture ABI. The stack
now issues v2 Ed25519-attested receipts and result artifacts. A digest can show
content integrity but cannot identify the issuer, and a grounded owner review
still cannot stand in for source identity, central proof, or owner acceptance.

## Decision

Pin exactly one active stack canary public key in the surface-catalog owner
contract. The stats owner accepts only v2 receipts and artifacts whose
content addresses and Ed25519 attestations both verify against that key at the
reviewed owner revision.

Keep three evidence stages distinct:

1. a clean-source receipt identifies the committed derived catalog surface;
2. the existing owner review validates one captured catalog and its watermark;
3. a bounded projector carries only endpoint, freshness, and grounded-canary
   fields into a stack overlay.

The source digest identifies the catalog bytes served by this MCP contour. It
does not make catalog rows authoritative owner facts. None of these stages may
issue central proof, owner acceptance, admission, rollback, or higher effects.

## Options Considered

- Continue accepting unsigned v1 captures because they are content-addressed.
- Read the public key from the runtime that produced the capture.
- Pin the issuer in owner source and preserve separate source/review/projection stages.

## Rationale

The third route prevents a captured artifact from authenticating itself and
keeps every authority transition explicit. It also lets the stack consume one
typed owner overlay without moving stats meaning or acceptance into the
runtime plane.

## Consequences

- Existing v1 captures are intentionally unsupported.
- Signer rotation requires an owner-source review before new captures are trusted.
- Dirty source cannot issue an exact source identity receipt.
- A stale catalog can remain grounded while freshness is blocked.
- Stats remains shadow until separate central proof, owner acceptance, and rollback gates exist.

## Source Surfaces

- `stats/surface-catalog/CODEX_MCP.md`
- `stats/surface-catalog/runtime_capture_trust.json`
- `schemas/stats-mcp-source-identity-receipt.schema.json`
- `scripts/issue_stats_mcp_source_identity.py`
- `scripts/review_stats_mcp_result.py`
- `scripts/project_stats_mcp_owner_review.py`
- `tests/test_stats_mcp_source_identity.py`
- `tests/test_stats_mcp_owner_review.py`
- `tests/test_stats_mcp_owner_review_projection.py`
- `aoa-sdk:schemas/organ-access/organ-owner-result-review.schema.json`
- `abyss-stack:mcp/services/abyss-stack-mcp/src/abyss_stack_mcp/canary.py`

## Validation

Run the focused MCP owner-evidence tests, source-home and mechanics topology
validators, decision-index generation/check, repository validation, and the
full release gate. Live validation must use a post-landing clean owner revision.
