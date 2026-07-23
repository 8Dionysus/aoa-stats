# Owner source return

Use this procedure after the bundle is applicable and before any owner-relative
read. It locates one canonical owner and then selects a bounded authored route;
it is not a repository-discovery search.

## Resolve the owner

1. Inspect exactly `<bundle_dir>/.aoa-skill-source.json` in one tool turn that
   contains no other read or command.
2. When it exists, require:
   - schema `aoa_skill_source_receipt_v1` or
     `aoa_skill_source_receipt_v2`
   - bundle and source name `aoa-stats`
   - owner `aoa-stats`
   - version `0.2.2`
   - an existing absolute `owner_root`
   - safe relative `source_path`
   - `<owner_root>/<source_path>/SKILL.md`
   - for v2, non-empty `digest`, `source_fingerprint`,
     `source_fingerprint_scope`, and `prompt_description_sha256`; preserve
     `capability_graph_hash` when present
3. An invalid or mismatched existing handle is terminal:
   `blocked_missing_owner_source`. Do not try another checkout.
4. Only when that exact handle does not exist, run
   `git -C <bundle_dir> rev-parse --show-toplevel` once and use that root.
5. In the next isolated tool turn, read only
   `<owner_root>/skills/port.manifest.json`. Require owner `aoa-stats`, this
   bundle name, and the same source path. A manifest read batched with an owner
   document is not an observed gate and terminates
   `blocked_owner_source_gate_not_observed`.
6. Treat handle schema, commit, dirty posture, digest, source fingerprint,
   capability graph hash, and prompt-description hash as location provenance,
   not parity, currentness, or source authority.

Never use parent traversal, sibling scans, `find`, `rg --files`, a
repository-wide `rg`, workspace conventions, `.system`, another skill
directory, or a temporary fixture to discover a substitute owner.

## Separate source and live runtime

`<owner_root>` above is the source checkout for this procedure. Never infer a
current OS runtime, live federation root, or owner-data location from its
parent directory. A clean checkout and an isolated worktree are equally valid
source roots and can have different parents.

For a current/live question:

1. Read the selected mechanic's authored runtime guide or contract.
2. Prefer an explicit runtime root supplied by the request. Otherwise inspect
   the owner-named deployed read-only runtime surface declared by that guide.
3. Require an observed absolute runtime repository root, its exact command,
   and any explicit data/workspace/federation-root argument. When the deployed
   command intentionally uses the owner's documented default, derive that
   default from the deployed runtime repository, not from `<owner_root>`.
4. Validate the exact runtime script, authored registry/profile, and live
   output paths under that observed runtime root before using them. Check the
   runtime script's path and command identity; do not read its implementation
   unless the selected task diagnoses that script itself.
5. Stop `blocked_missing_live_runtime_root` when only source or intended
   deployment documentation is available. Do not call a source-worktree
   command result live evidence.

Report `procedure_source_root`, `runtime_repo_root`, and `live_data_root`
separately. A deployed unit's active state proves only its runtime posture; it
does not prove publisher freshness, observation freshness, or owner coverage.

## Choose the smallest authored route

After manifest success, match one route before reading owner content:

| Question | First authored route | Follow only |
| --- | --- | --- |
| Measurement identity or compatibility | `stats/measurement-contract/README.md` | The named schema and pure implementation route declared there. |
| Owner stats-port compatibility or landed coverage | `stats/federation/README.md` | The central protocol or owner inventory, then a named owner's port when needed. |
| Receipt-envelope or event-kind admission | `stats/intake-contract/README.md` | The named registry/schema and supplied receipt. |
| Named public or deferred read model | Exact record under `stats/read-models/{active,deferred,retired}/` | Its declared owner inputs, mechanic routes, schema, and output. |
| Named non-catalog operation | Exact record under `stats/operation-contracts/active/` | Its reciprocal part in `mechanics/topology.json`. |
| MCP or other stats access | `stats/surface-catalog/CODEX_MCP.md` | The named authored profile or operation behind the returned projection. |
| Unknown stats surface | `stats/source_home.manifest.json` | At most `mechanics/topology.json` and `generated/summary_surface_catalog.min.json` to resolve one owner route. |

If the bounded three-index fallback cannot identify one route, stop
`blocked_missing_owner_route`. Do not widen into repository archaeology.

## Live publisher and source-coverage route

For a question about registered live publishers, their current presence,
freshness, or owner coverage, use this exact bounded chain:

Exception: the `Undefined cross-owner score` path in `evolve.md` is a
structural missing-meaning decision, not a live publisher observation. Its
four-source route overrides this chain; do not load the runtime guide,
admission decision, deployed units, live output, or audit command for that
case.

1. Read:
   - `stats/read-models/active/source_coverage_summary.profile.json`
   - `mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json`
   - `mechanics/recurrence/parts/live-receipt-refresh/CONTRACT.md`
   - `mechanics/recurrence/parts/live-receipt-refresh/docs/LIVE_SESSION_USE.md`
   - `docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md`
2. For a current OS claim, inspect the deployed
   `aoa-stats-live-refresh.service` and `.path` read-only. Resolve their
   runtime repository and federation root using the source/runtime separation
   above. If they are not installed and no explicit runtime root was supplied,
   stop instead of substituting `<owner_root>`.
3. Run the deployed runtime audit with this exact argv:
   `python <runtime_repo_root>/scripts/check_live_publishers.py --registry
   <runtime_repo_root>/mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json
   --federation-root <live_data_root> --require-non-empty`.

4. Read the deployed live output
   `<runtime_repo_root>/state/generated/source_coverage_summary.min.json`.
   Read `<runtime_repo_root>/generated/source_coverage_summary.min.json` only
   as a committed reference comparison.
5. Classify the profile, registry, and mechanic contract as authored meaning;
   the audit as current publisher presence/compatibility; the live output as a
   derived observation; and the committed output as a weaker reference
   snapshot.
6. Inspect both summaries' `generated_from`,
   expected/missing/unexpected owners, counts, thin-signal flags, and their
   file modification times. Extract only those fields and the owner rows
   needed by the question; do not dump the receipt feed. Keep these claims
   separate:
   - publisher availability and parseability come from the audit
   - declared-owner coverage comes from the registry-backed live output
   - observation freshness comes from the receipt timestamps and an authored
     freshness window
   - artifact refresh time says when the projection was rebuilt, not when its
     evidence was observed
7. If no authored freshness window or expectation exists, return freshness as
   `unknown` even when the audit is green and the live artifact was rebuilt
   recently.
8. Return only the bounded currentness and coverage answer. Do not enumerate
   every repository, scan for alternative ports, run the full release gate, or
   repair missing publishers. Do not open
   `state/generated/summary_surface_catalog.min.json`, another read-model
   output, or another profile for this route.

Report the source route, owner root, handle schema and identity dimensions or
git action, manifest action, first owner-read action, procedure source root,
runtime repo root, live data root, selected authored route, command result, and
skipped checks.
