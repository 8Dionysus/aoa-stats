# Review Captured Stats Catalog In The Owner

## Index Metadata

- Decision ID: AOST-D-0015
- Original date: 2026-07-28
- Surface classes: stats/surface-catalog, MCP/access, owner evidence
- Stats surfaces: summary surface catalog, grounding review, freshness watermark
- Source lanes: aoa-stats, aoa-sdk, abyss-stack, aoa-evals
- Guard families: derived-only authority, exact capture binding, freshness, no acceptance inference
- Posture: accepted

## Context

The stack-owned MCP can authenticate a `stats_catalog` call and preserve its
structured result, but transport success cannot prove that the payload matches
the current stats owner contract or selected owner catalog. The committed and
live catalogs also carry different data ages, so schema validity and freshness
must remain distinct.

Letting the stack or central eval layer infer those claims would move
statistical meaning out of `aoa-stats`.

## Decision

Keep runtime capture and stats-owner review separate.

`abyss-stack` captures one bounded, untrusted `stats_catalog` result.
`aoa-stats` validates the exact content-addressed artifact against
`schemas/summary-surface-catalog.schema.json`, resolves its declared committed
or live owner catalog, requires exact content equality, and issues the shared
SDK owner-review receipt.

Grounding and freshness are independent. Exact equality can ground the
catalog, while `generated_from.latest_observed_at` can still block freshness
when the underlying receipt feed is old. The receipt keeps owner acceptance,
central proof, admission, cross-organ proof, and rollback structurally false.

## Options Considered

- Let the MCP runtime attest catalog meaning.
- Let central evals infer grounding and freshness from call success.
- Preserve exact runtime capture, then issue a separate stats-owner review.

## Rationale

The third route preserves thin access and derived-only authority. Stats owns
the catalog schema, selected owner bytes, and watermark interpretation; stack
owns capture and lifecycle; SDK owns only the shared receipt shape; evals
compose evidence without becoming the statistical owner.

## Consequences

- A valid but old catalog is explicitly grounded and freshness-blocked.
- Schema or selected-owner byte drift produces an explicit rejected review.
- A live catalog without an explicit revision-matched owner runtime root is
  blocked; the procedure source checkout is never substituted for runtime
  evidence.
- Freshness can become exact only after a current owner receipt watermark is
  present in the selected catalog.
- A valid review does not accept or admit the stats organ.
- Other stats MCP operations need separate owner result contracts before they
  can claim result grounding.

## Source Surfaces

- `stats/surface-catalog/CODEX_MCP.md`
- `schemas/summary-surface-catalog.schema.json`
- `generated/summary_surface_catalog.min.json`
- `scripts/review_stats_mcp_result.py`
- `tests/test_stats_mcp_owner_review.py`
- `docs/decisions/AOST-D-0016-authenticate-and-separate-stats-mcp-owner-evidence.md`
- `aoa-sdk:schemas/organ-access/organ-owner-result-review.schema.json`
- `abyss-stack:mcp/services/abyss-stack-mcp/src/abyss_stack_mcp/canary.py`

## Validation

Run the focused owner-review tests, summary-catalog schema/build checks,
decision-index generation/check, repository validation, and the full release
gate. Cross-repository integration must additionally validate a produced
receipt against the exact SDK schema.
