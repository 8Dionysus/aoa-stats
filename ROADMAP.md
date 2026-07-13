# aoa-stats roadmap

> Current release: `v0.1.3`

This is the current repo-owned direction surface. Shipped history belongs in
`CHANGELOG.md`; durable rationale belongs in `docs/decisions/`; the public
snapshot lives at `README.md#current-v0-surface`.

## Current direction

The current line is federated statistical measurability: establish one small
compatible grammar, let every active owner define meaningful local measures,
and keep cross-repo views useful while weaker than source-owned receipts,
proof, rollout history, runtime state, and owner decisions.

Work advances through alternating cross-slices between the authored `stats/`
source home and the repeatable operations under `mechanics/`. Each slice has
one lead, strengthens one real boundary, updates only the reciprocal route it
needs, and leaves the next slice to reverse the lead.

## Priority sequence

1. **Measurement protocol.** Keep identity, population, sample, unit,
   dimensions, aggregation, missingness, uncertainty, provenance, reporting,
   privacy, and live/reference posture explicit and versioned.
2. **Owner federation.** Grow root `stats/` ports from real owner questions and
   consumers. Return only proven common requirements to the central contract;
   keep unique meaning local.
3. **Current owner inputs.** Re-ground authored receipts, profiles, examples,
   reports, and local packets on canonical owner paths. Keep compatibility only
   for an evidenced current consumer, then remove translations and fallbacks.
4. **Source meaning.** Make every public read model or non-catalog observation
   state one bounded question, exact input posture, stronger-owner chain,
   consumer risk, and authority ceiling under `stats/`.
5. **Mechanic ownership.** Keep repeatable config, docs, examples, supporting
   schemas, scripts, and focused proof with the nearest real mechanic part.
   Reuse a common parent only when the operation shape is genuinely shared.
6. **Live admission.** Admit a profile or packet to live materialization only when
   both a current owner source and a refresh-observation route exist. Missing,
   stale, or malformed evidence stays visible and never triggers example
   fallback.
7. **Publication integrity.** Preserve stable public schema and generated paths
   where consumers depend on them, rebuild deterministic outputs from authored
   sources, and keep retired records limited to cleanup and provenance.
8. **Single thin access plane.** Move stats MCP transport into the stack-owned
   service after direct and MCP reads prove one semantic identity. Remove the
   repo-local server after consumer cutover; the statistical core remains
   independent of MCP runtime.

## Authority routes

| Need | Authoritative route |
| --- | --- |
| repository shape and edit law | `DESIGN.md` and `AGENTS.md` |
| shared measurement grammar | `stats/measurement-contract/` |
| local-port compatibility and owner coverage | `stats/federation/` |
| authored stats-family map | `stats/README.md` and `stats/source_home.manifest.json` |
| exact read-model lifecycle and input posture | target record under `stats/read-models/` |
| non-catalog observation maturity | target record under `stats/operation-contracts/` |
| operation ownership and placement | `mechanics/README.md`, `mechanics/topology.json`, and the target part |
| public derived discovery | `generated/summary_surface_catalog.min.json`, checked against authored profiles |
| receipt admission | `stats/intake-contract/` |
| live materialization and cleanup | active profile selectors plus the live-refresh mechanic named by topology |
| stable authority and strength vocabulary | `docs/BOUNDARIES.md`, `docs/ARCHITECTURE.md`, and `stats/surface-catalog/SURFACE_STRENGTH_MODEL.md` |
| durable rationale | `docs/decisions/README.md` and its generated indexes |
| shipped chronology | `CHANGELOG.md` and Git history |

The roadmap does not repeat the current catalog roster, lifecycle counts,
part-by-part payload inventory, or compatibility chronology. Follow the routes
above for exact current state.

## Slice completion

A bounded slice is handled when:

1. the source-owned fact and consumer are explicit;
2. one authored source record and one real operation route agree in both
   directions;
3. payload and focused proof live with their owner;
4. generated and compatibility surfaces are rebuilt or intentionally unchanged;
5. source-home, mechanics, decision, public-contract, and release validation
   pass; and
6. the report states what remains reference-only, deferred, retired, or still
   dependent on a stronger owner.

## Non-goals

The roadmap is not to widen into a dashboard empire, global score, hidden
scheduler, proof engine, route controller, memory owner, or runtime authority.
No summary may outrank the owner sources named by its profile. Rollout summaries
remain weaker than source-owned rollout history and rollback decisions.

## Release gate

Release commands stay in [`docs/RELEASING.md`](docs/RELEASING.md); the normal
repository gate stays in [`AGENTS.md#verify`](AGENTS.md#verify).
