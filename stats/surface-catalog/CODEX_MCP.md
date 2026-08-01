# Stats MCP read contract

## Ownership

`aoa-stats` owns the transport-neutral meaning and authority ceiling of public
stats reads. The stack-owned `aoa-stats-mcp` service implements that contract;
the project Codex plane owns registration under the stable name `aoa_stats`.

The access plane is read-only and non-sovereign. It does not own a measurement,
owner-local definition, evidence, freshness, verdict, route, workflow, or
permission to act. The statistical core remains usable when MCP is absent.

## Public access shape

The read contract permits bounded access to:

- the owner-produced derived-surface catalog
- one catalog-listed surface with explicit reference or live-materialization
  posture
- the central authority and source-owner boundary references
- the federated owner inventory and one owner-local port definition
- compatibility findings for a caller-provided measurement contract and packet

Catalog and owner-port reads return owner-authored definitions or derived
projections, not attested truth. Packet checking reports compatibility only;
it preserves the same semantic identity as the direct packet reader without
attesting the packet's evidence or freshness.

Missing, stale, unknown, and reference-only states remain explicit. Access must
stay bounded and must not expose raw session material or sensitive owner
content.

## Owner routes

- Statistical semantics and direct read contract: `stats/measurement-contract/`
  and `scripts/read_measurement_packet.py`
- Catalog meaning and authority ceiling: `stats/surface-catalog/`
- Owner coverage and local-port compatibility: `stats/federation/`
- Runnable MCP service and exact tool surface:
  `abyss-stack/mcp/services/aoa-stats-mcp/`
- Project registration and wrapper: the Codex-plane owner in `8Dionysus`

The former repo-local MCP package, launcher, optional dependency, resources,
prompts, and live-source-registry access are retired. Reintroducing them would
create a second access implementation and violate the single-owner boundary.

## Owner review of a captured catalog

An authenticated `stats_catalog` call remains runtime evidence only.
`abyss-stack` may preserve the exact result as a private, untrusted,
content-addressed artifact. `scripts/review_stats_mcp_result.py` then verifies
the capture binding, validates the payload against
`schemas/summary-surface-catalog.schema.json`, and requires byte-semantic
equality with the owner-selected committed or live catalog.

Reviewing a live `state/generated/` result requires an explicit
`--owner-runtime-root`. The reviewer validates that runtime checkout's exact
Git revision against the requested owner source revision and blocks when the
root is absent or drifted; it never substitutes the procedure source worktree
as live evidence.

The owner review uses `generated_from.latest_observed_at` as its provider
watermark. A schema-valid exact catalog may be grounded while still failing
freshness when its underlying receipts are old. The receipt does not assert
stats acceptance, central proof, admission, cross-organ benefit, or rollback.

Current stack captures use the v2 receipt and result-artifact ABI. Both are
Ed25519-attested and are trusted only through the single active public key in
`stats/surface-catalog/runtime_capture_trust.json` at the reviewed owner
revision. Content addressing alone is not issuer authentication.

`scripts/issue_stats_mcp_source_identity.py` separately identifies the clean
committed catalog surface used by this access contour. Its digest describes
the derived catalog bytes; it does not turn catalog rows into source truth.
After an exact owner review,
`scripts/project_stats_mcp_owner_review.py` may project only endpoint,
freshness, and grounded-canary evidence into the stack overlay. Neither path
issues central proof, owner acceptance, admission, or rollback.
