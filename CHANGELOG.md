# Changelog

All notable changes to `aoa-stats` will be documented in this file.

The format is intentionally simple and human-first.
Tracking starts with the first public release-prep baseline for this repository.

## [Unreleased]

### Added

- Added the root design spine for the staged source-home and mechanics
  refactor, including the authority split and alternating cross-mode.
- Added explicit route homes for stats-authored source families and evidenced
  repeatable mechanics, with machine-readable crosswalk validation.
- Added authored read-model profiles under `stats/read-models/`; the public
  summary catalog is now projected from those profiles instead of a hardcoded
  Python catalog table.
- Added `stats/operation-contracts/` so every active non-catalog mechanic part
  has a reciprocal source-family route without inventing a public profile.
- Added one schema-backed authored operation record for each of the 15 active
  non-catalog mechanic parts, with exact reciprocal topology links and honest
  input-maturity, authority-ceiling, consumer-risk, and owner-return posture.
- Replaced generic via-negativa and Titan memory/runtime cards with their
  actual checklist-only, schema/documentation, and documentation-only maturity
  boundaries.
- Added active mechanic packages and focused part contracts for Agon,
  Antifragility, Audit, Boundary Bridge, Checkpoint, Experience, Growth Cycle,
  Method Growth, Recurrence, Release Support, RPG, and Titan.
- Added source-authored retired read-model tombstones so an output can leave
  active publication while its former name remains in deterministic stale-file
  cleanup and its rationale remains discoverable.
- Added stable catalog-slot reservation to retired profiles so lifecycle
  removal cannot silently renumber later authored surfaces or reuse a former
  identity.

### Changed

- Centralized active validation and test commands in owner `AGENTS.md`, part
  `VALIDATION.md`, and the primary release, live-use, and MCP guides. Other
  active Markdown now routes to those owners, with a repo-wide docs guard
  preventing command blocks from drifting back into weaker surfaces.
- Replaced named Source Coverage and Method Growth proof-route assertions with
  one topology-derived read-model rule: every part that declares a localized
  test district must contain focused tests and expose at least one of them
  through the source-family validator routes.
- Removed the hand-maintained mechanic package roster from topology tests.
  Package activation now proves non-empty parity between the canonical
  topology activation map, active package records, and materialized root
  directories while the mechanics README remains a human route atlas.
- Removed fixed non-catalog operation counts from source-home and mechanics
  topology proof while preserving non-empty inventory, unique record binding,
  schema validation, and exact record/manifest/part reciprocity. A functional
  growth probe now proves the operation family can expand without editing a
  cardinality assertion.
- Reduced the root repository validator's direct text inventory to stable
  repo-wide entrypoints; stats-family and mechanic document membership now stay
  exclusively with the source-home, topology, and part validators already run
  by that command.
- Moved exact catalog consumer-return and artifact trust-lifecycle assertions
  from the root catalog test to their Boundary Bridge and Release Support
  owners, preserving the checks while leaving root proof focused on the shared
  authored/public catalog contract.
- Removed fixed active/deferred/retired profile counts from source-home
  validation while preserving non-empty active publication, stable slot, retired
  reservation, schema, route, and generated-catalog parity checks. A functional
  growth probe now proves valid lifecycle inventory can expand without editing
  validator code.
- Reduced the root build-view proof to profile-derived fan-out and complete
  committed-byte parity, removing the second hand-maintained suite of
  mechanic-owned field assertions while retaining part-local semantic and
  invariant coverage.
- Localized the surface-strength vocabulary under its `stats/surface-catalog`
  source owner, removed changing Antifragility Vector posture from the shared
  model, and made catalog proof reject vocabulary drift from active and deferred
  authored profiles while updating the public catalog reference atomically.
- Returned live-refresh inventory truth to authored read-model profiles:
  mechanic contracts and operator guidance now describe profile-derived set
  rules without copied counts or complete rosters, while part-local proof loads
  active and retired records directly and the root docs suite no longer owns
  operation-specific inventory parity.
- Localized derived-signal precedence and anti-loop guidance under the
  Boundary Bridge consumer-regrounding part, replacing the Wave-4 root document
  with a mechanic-owned route and focused proof.
- Slimmed the public root and documentation entrypoints into stable route and
  architecture surfaces; exact lifecycle state now stays with authored
  profiles, operation records, mechanic parts, topology, and indexed decisions
  instead of being replayed as changing counts and named rosters.
- Reworked the root agent route so structural changes start from `DESIGN.md`,
  then cross-route `stats/` source meaning with `mechanics/` operations while
  preserving active root compatibility surfaces.
- Localized operation-owned config, docs, examples, manifests, supporting
  schemas, systemd templates, scripts, and focused tests below their mechanic
  parts. Root schemas and generated summaries remain stable public
  publication surfaces; root commands and docs now require an explicit
  repo-wide or compatibility role.
- Reclassified the former flat root guidance as historical provenance and
  made the active documentation map route directly to source and mechanic
  owners.
- Refreshed the derived memory movement summary so the reviewed KAG/ToS bridge
  object from `aoa-memo` is visible as a `reviewed_corpus` bridge consumer ref.
- Added a read-only memory route boundary to the memory movement summary so
  `aoa-stats` names `.aoa` evidence, local memo-port candidates, MCP dry-run
  access, and `aoa-memo` durable landing limits without becoming memory
  authority.
- Pinned CI to the `abyss-machine` trust-admission hardening that enforces the
  required pre-materialization subject-store deny before the verified allow
  roundtrip.
- Moved the shared Method Growth candidate-lifecycle projection and its focused
  tests out of the root builder/test monoliths into the importable builder core
  and the `mechanics/method-growth/` package while preserving public outputs
  and the root build compatibility facade.
- Moved the shared Growth Cycle fork, session-branch, automation-pipeline, and
  automation-followthrough projections plus focused invariant tests out of the
  root monoliths into an importable mechanic core while preserving public
  schemas, generated routes, and the root build facade.
- Made authored `live_state_capable` profiles drive the local live-output
  inventory, separated the committed Component Refresh reference adapter from
  its pure projection, and stopped fixture-only component posture from being
  materialized or advertised as live state while retaining stale-file cleanup.
- Reframed Continuity Window as a committed cross-owner reference projection,
  separated its source adapter from filesystem-free validation/projection, and
  removed status-only reanchor success inference while excluding the static
  example chain from local live state.
- Reclassified Codex Plane Deployment as a committed owner-example reference,
  separated its reference and deploy-local source contracts, and stopped
  missing runtime rollout evidence from falling back to examples in live state.
- Separated checked-in trusted rollout history from Codex Plane Deployment and
  from cadence examples, localized strict history and cadence projection seams
  under their mechanic owners, and removed all four committed companion
  summaries from live-state admission while retaining managed stale cleanup.
- Required live-admitted profiles to have both a current owner source and an
  observable refresh route; kept Memory Movement, Owner Landing, and Stress
  Recovery as committed/reference snapshots until their missing corpus trigger
  or real owner publishers exist, while preserving stale live-output cleanup.
- Separated Memory Movement and Stress Recovery projection rules from their
  filesystem adapters so the Boundary Bridge and Antifragility mechanic owners
  can carry focused invariants while the root builder remains a compatibility
  facade.
- Re-grounded the Stress Recovery committed receipt, profile, mechanic
  examples, and generated read model on the current mechanic-owned `aoa-evals`
  path, then removed the retired bundle-path translation from the source
  adapter. The surface remains a false-live draft/reference projection under
  AOST-D-0004; exact source resolution no longer carries a migration fallback,
  and repository validation pins the owner revision that carries current
  sibling refs inside the report.
- Reduced the root roadmap to durable direction, owner routes, and alternating
  cross-slice priorities. Exact catalog rosters, lifecycle counts, mechanic
  payload lists, and compatibility chronology now stay with their authored or
  generated owners, and focused tests reject their return to the roadmap.
- Moved the shared Audit object, core-skill application, and surface-detection
  projections plus focused invariant tests out of the root builder/test
  monoliths into explicit object and shared core-skill observation cores while
  preserving public outputs, live receipt posture, and root compatibility
  aliases.
- Returned Source Coverage aggregation proof from the Boundary Bridge consumer
  and root integration tests to its Audit owner part, adding ordering,
  conservation, non-mutation, registry-baseline, and authority-stop invariants
  without changing public bytes or live admission.
- Clarified the Route Progression owner chain and moved its seven-axis receipt
  aggregation plus focused invariants into an RPG-owned core and part-local
  test boundary while preserving the public output and root compatibility
  aliases. Reclassified the surface as reference-only because the current
  owner receipt is semantic rather than numeric, rejected score invention, and
  made live refresh omit and clean the legacy snapshot.
- Corrected consumer re-grounding inputs to lead with the exact current
  `aoa-skills` semantic progression schema and example, and replaced an active
  owner-landing bootstrap label with source-route compatibility wording. The
  historical receipt ABI and committed summary payloads remain unchanged.
- Localized Runtime Closeout aggregation and focused invariants under the
  Checkpoint mechanic while retaining root compatibility aliases. Reclassified
  the surface as reference-only because the admitted wave-closeout receipt and
  former live feed no longer match the current `abyss-stack` trial-closeout
  producer, removed that stale feed from active admission, and preserved it as
  committed compatibility only. No implicit event-kind alias was introduced
  and committed Runtime Closeout bytes remain stable.
- Corrected the Repeated Window source question from inferred change to
  observed calendar-date activity, then localized its filesystem-free
  aggregation core and focused permutation, conservation, identity,
  non-mutation, schema, compatibility-hook, and public-byte invariants under
  Recurrence.
- Re-grounded Titan Incarnation in the exact checked-in `aoa-agents` roster
  examples and `aoa-sdk` session-receipt example, with cross-owner coherence
  validation before count projection. Reclassified Titan Summon's static
  zeros as an explicit no-observed-ledger compatibility baseline rather than
  evidence of zero activity, while keeping both surfaces reference-only.
- Retired the no-input Titan Summon compatibility baseline from active build,
  catalog, committed output, and root facade surfaces. Kept a minimal
  source-home tombstone and the former schema so stale live copies are removed
  without preserving a content-free read model as active observability.
- Retired the example-only Owner Landing aggregate after verifying that no
  current owner publishes its receipt kinds and no direct consumer requires
  the standalone payload. Kept those event kinds and their normalization as
  active Supersession Drop inputs, removed the now-empty dedicated mechanic
  part, and preserved the public schema as contract history.
- Changed `catalog_order` from a dense position to a stable slot, restoring
  Titan Summon's former slot 21 and reserving Owner Landing's former slot 4 in
  retirement tombstones while leaving later active profile identities intact.
- Returned Method Growth producer proof from the package-level test district
  to Candidate Lineage and Supersession Pruning part-local test homes while
  keeping their genuinely shared normalization core and all public generated
  bytes unchanged.
- Retired the historical Runtime Closeout wave snapshot after verifying that
  current owners publish distinct trial and return ABIs and no direct consumer
  requires the standalone payload. Kept the wave event kind as generic Object,
  Repeated Window, and Source Coverage evidence, reserved catalog slot 22 for
  cleanup, preserved the public schema as contract history, and removed the
  now-empty repo-local Checkpoint mechanic package.
- Returned Receipt ABI loading, deduplication, admission, and conservative
  supersedes-resolution proof from the root build suite to the Boundary Bridge
  crossing part while retaining the root build facade and public envelope
  paths unchanged.
- Grounded the deferred Antifragility Vector in the exact ATM10-Agent stressor
  publisher/contracts and draft aoa-evals posture surfaces, projected its
  input posture, stronger-owner inputs, consumer risk, and four activation
  gaps into the public catalog, and moved its schema/example proof from the
  root suite into the mechanic part. The candidate remains non-active, with a
  suppressed null-vector example and no builder, output, live registration, or
  MCP promotion.
- Returned the retained Trusted Rollout missing-latest-ref facade fallback
  proof from the root build suite to the Release Support owner part. The pure
  core remains strict, the root helper keeps its compatibility behavior, and
  public summaries, profiles, generated bytes, and live admission are
  unchanged.
- Removed eight unreferenced root build-facade helpers left after the trusted
  rollout, cadence, component refresh, Titan, and memory adapter extractions.
  Canonical mechanic-owned adapters, current zero-argument builders, tested
  legacy seams, CLI/fan-out behavior, profiles, and generated bytes remain
  unchanged.
- Removed nine unreferenced Component Refresh vocabulary and pure-helper
  re-exports from the root build facade. The mechanic-owned core remains the
  canonical import surface while the evidenced zero-argument adapter, builder,
  committed output, and public schema stay unchanged.
- Localized proof of the Via Negativa review checklist under its Antifragility
  part, aligning pruning order, owner-review, surviving-provenance, and
  proof-failure stop lines with the common center while keeping the operation
  checklist-only, `symbolic_unbound`, non-mutating, and outside MCP/runtime
  activation.
- Slimmed root and stats source-home guidance into owner-routing atlases:
  exact surface state remains in authored profiles and operation records,
  mechanic behavior remains part-local, and durable rationale remains in
  indexed decisions instead of being replayed as a drifting status roster.
- Removed the three migration-era root documentation redirects for Candidate
  Lineage, Component Manifests, and Component Refresh after active repository
  and central provenance routes were re-grounded on their part-local owners.

## [0.1.3] - 2026-04-23

### Summary

- this patch expands derived observability across Agon prebindings,
  verdict-delta scars, mechanical trials, retention rank, schools/lineages,
  KAG/Sophian signals, and Wave XV epistemic stats
- recurrence derived summaries, consumer re-grounding signals, Titan metrics,
  Experience micro-friction, release summaries, adoption metrics, governance
  stats, regression summaries, and Titan incarnation summaries are added or
  tightened
- `aoa-stats` remains a downstream derived layer that summarizes owner-owned
  evidence without becoming workflow, proof, memory, routing, or runtime truth

### Added

- Agon observability surfaces for court/memo/stats prebindings, scar deltas,
  mechanical trials, retention rank, schools/lineages, KAG/Sophian, and
  epistemic waves
- recurrence derived summary contracts, consumer re-grounding signals,
  live-surface registration, Titan metrics, Titan incarnation summaries,
  Experience micro-friction, release, adoption, governance, and regression
  summary surfaces

### Changed

- stats review follow-ups, contract drift, recurrence projection schemas,
  regression summary metric schemas, consumer re-grounding freshness, and live
  derived-surface registration were tightened

### Validation

- The repository release gate passed for this release.

### Notes

- this patch keeps observability derived and evidence-bound; owner repos still
  decide what events, verdicts, memories, and runtime records mean

## [0.1.2] - 2026-04-19

### Summary

- this patch hardens intake governance and extends the summary catalog with
  component-refresh and stress-recovery reporting
- memo writeback receipts, live MCP surface preference, and freshness handling
  are tightened across the derived observability lane
- `aoa-stats` remains a bounded derived layer rather than workflow authority

### Added

- component refresh summary surfaces, chaos wave 1 stress-recovery summaries,
  and intake-governance plus summary-catalog upgrades
- memo growth writeback receipt acceptance and live stats surface preference
  in the repo-local MCP lane

### Changed

- decision-only component-refresh freshness, roadmap/current-direction docs,
  and CI/protection surfaces are tightened around current summary outputs

### Validation

- The repository release gate passed for this release.

### Notes

- this patch expands derived observability coverage while keeping source-owned
  rollout, memory, and runtime history authoritative elsewhere

## [0.1.1] - 2026-04-12

### Summary

- this patch adds repo-local Codex MCP disclosure and new rollout/continuity
  summary surfaces
- release-audit continuity dependencies and rollout builder behavior are
  hardened across the derived observability lane
- `aoa-stats` remains a bounded derived layer rather than workflow authority

### Added

- narrow repo-local `aoa_stats` MCP surface for Codex under
  `src/aoa_stats_mcp/` and `scripts/aoa_stats_mcp_server.py`, scoped to the
  summary catalog, generated surfaces, source registry, and boundary bundle
- focused MCP state tests under `tests/test_aoa_stats_mcp_state.py`
- optional MCP dependency surface in `requirements-mcp.txt`

### Documentation

- repo-local MCP posture and launch guidance in `stats/surface-catalog/CODEX_MCP.md`
- README, docs map, and AGENTS routing updates so the MCP stays bounded and
  visibly derived-only

### Changed

- added Codex rollout operations summaries, campaign cadence summaries, and
  continuity-window summaries to the derived observability layer.
- wired release-audit continuity dependencies, fixed continuity-summary
  discovery, and hardened rollout stats builders.

### Validation

- The repository release gate passed for this release.

### Notes

- detailed Codex MCP, rollout-summary, and continuity-summary changes for this patch remain enumerated below under `Added`, `Documentation`, and `Changed`

## [0.1.0] - 2026-04-10

First public release of `aoa-stats` as the derived observability layer in the
AoA public federation.

This changelog entry uses the release-prep merge date.

### Summary

- current public stats posture ships as a bounded derived layer rather than a
  dashboard authority or score empire
- the first public baseline includes the canonical shared receipt envelope,
  deterministic builders, local live-refresh helpers, and committed
  machine-first summary surfaces
- release messaging remains intentionally modest: counts, progression deltas,
  and summary capsules stay weaker than the source-owned receipts, verdicts,
  and workflow meaning they summarize

### Added

- first public release of `aoa-stats` as a repository for derived summary
  schemas, builders, validators, and generated observability surfaces
- canonical shared receipt-envelope and event-kind contracts under `schemas/`
- live receipt source registry plus local refresh, publisher-audit, and
  systemd watcher helpers under `config/`, `scripts/`, and `systemd/`
- committed generated summary surfaces under `generated/`, including the
  runtime-entry summary catalog capsule
- public-safe example receipt feeds and summary examples under `examples/`
- repo-level release, contribution, conduct, and security guidance for public
  release readiness

### Included in this release

- `10` committed generated summary surfaces under `generated/`
- current stats-layer docs under `docs/`
- current schemas, examples, scripts, tests, and live-refresh support files
- derived summary buildout across `generated/`, `schemas/`, `config/`,
  `scripts/`, `systemd/`, `examples/`, and `docs/`, including core-skill
  application summaries, supersedes-aware active views, surface-detection
  summaries, antifragility vectors, stress-recovery summaries, and the v2
  runtime capsule
- repo operating surfaces under `.agents/`, `.github/`, `AGENTS.md`,
  `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`,
  `tests/`, and `requirements-dev.txt`, including validate workflow, publisher
  audits, boundedness tightening, and release-ready community docs

### Validation

- Generated parity, repository validation, and the repository test suite passed
  for this release.

### Notes

- this remains a derived observability release, not a claim that `aoa-stats`
  now owns workflow, proof, route, or quest authority
- live local refresh stays operator-local under `state/`; the committed
  `generated/` directory remains the deterministic public repo surface
