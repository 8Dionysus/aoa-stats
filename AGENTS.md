# AGENTS.md

Root route card for `aoa-stats`.

## Purpose

`aoa-stats` is the derived observability organ for AoA. It consumes
source-owned receipts, evidence references, and bounded verdicts to build
deterministic read models without taking authority from their owners.

Dashboards are lanterns, not sovereigns.

## Owner lane

This repository owns:

- the stable meaning and contracts of stats-authored read models
- one authored question, evidence posture, authority ceiling, and owner-return
  route for each active non-catalog stats operation contract
- the shared receipt envelope and event-kind vocabulary needed by those models
- deterministic projection, refresh, and validation mechanics around those
  source contracts
- generated machine-first summaries and derived-only consumer access

It does not own:

- workflow, proof, practice, scenario, role, memory, runtime, route,
  quest-state, or self-agent truth
- mastery, intent, causality, or current truth inferred from volume alone
- source-owner facts merely because a stats projection can count them

## Start here

1. `README.md`
2. `DESIGN.md`
3. `stats/README.md` for the source-authored stats home
4. `mechanics/README.md` for repeatable operation topology
5. `ROADMAP.md`
6. `docs/BOUNDARIES.md`
7. `docs/ARCHITECTURE.md`
8. `docs/decisions/README.md` for durable rationale and lookup indexes
9. `mechanics/recurrence/parts/live-receipt-refresh/docs/LIVE_SESSION_USE.md`
   for the current receipt refresh route
10. `mechanics/recurrence/parts/component-refresh/docs/COMPONENT_REFRESH_SUMMARIES.md`
    for derived-only component refresh posture
11. `mechanics/release-support/parts/codex-deployment-rollout/docs/CODEX_PLANE_DEPLOYMENT_SUMMARIES.md`
    for committed-reference versus deploy-local Codex Plane posture
12. `mechanics/release-support/parts/trusted-rollout-history/docs/TRUSTED_ROLLOUT_HISTORY_SUMMARIES.md`
    for checked-in owner-history posture and its separation from deployment
    and cadence examples
13. `mechanics/release-support/parts/rollout-campaign/docs/ROLLOUT_CAMPAIGN_SUMMARY.md`
    and `mechanics/audit/parts/drift-shadow-review/docs/DRIFT_REVIEW_SUMMARY.md`
    for committed cadence-example posture
14. `mechanics/boundary-bridge/parts/memory-owner-handoff/docs/MEMORY_MOVEMENT_SUMMARY.md`
    for reviewed corpus movement posture
15. `mechanics/antifragility/parts/antifragility-vector/docs/ANTIFRAGILITY_VECTOR.md`
    for the only deferred read-model candidate and its activation gaps
16. the nearest nested `AGENTS.md` for every path you touch
17. `docs/history/AGENTS_ROOT_REFERENCE.md` only when historical pre-refactor
    guidance is needed as provenance

## Repository shape

`aoa-stats` has two cross-routed active homes:

- `stats/` owns source-authored stats meaning, source-family topology, and the
  contract that says what a derived read model is.
- `mechanics/` owns repeatable operations around those sources: intake,
  projection, refresh, recurrence, validation, and release support.

Operation payload lives below the nearest mechanic part. Root `schemas/` and
`generated/` are stable public publication districts; root `scripts/` and
`tests/` contain only repo-wide or compatibility surfaces. `docs/`,
`examples/`, and `manifests/` keep only repo-wide, decision, public bundle, or
explicit compatibility routes. The exact exception set is enforced by
`mechanics/topology.json` and `scripts/validate_mechanics_topology.py`.

A root script path may be stable without making every historical helper name a
permanent ABI. Keep a symbol-level compatibility export only when it has a
current caller, an explicit external contract, or focused owner-part proof.
After an adapter/core extraction, remove unreferenced path and mutable-tuple
helpers instead of preserving dead overcode inside `build_views.py`.

When several parts of one mechanic share deterministic receipt-to-read-model
rules, keep that reusable core under `src/aoa_stats_builder/`, declare its
focused package-level tests in `mechanics/topology.json`, and leave CLI, input
loading, output fan-out, and check/write policy in the root build facade.
Package-level proof is for genuinely cross-part invariants, not a convenient
home for unrelated producer behavior. When a shared core exposes distinct
read-model builders, return each builder's schema, ordering, conservation,
non-inference, and public-byte proof to the part that owns that output.

Method Growth keeps one shared candidate-lifecycle core because Supersession
Pruning consumes normalized Candidate Lineage and landing receipts. Candidate
Lineage and Supersession Pruning nevertheless own separate behavioral test
homes under their parts. No package-level test district is needed merely
because both builders live in one Python module.

The Audit receipt-observation cluster uses two explicit core boundaries. Core-skill
application and surface-strength detection share finish-stage
`core_skill_application_receipt` selection and one package-level test home.
Object observation separately summarizes the full admitted receipt set and
keeps its focused tests with its part. Both cores stay descriptive and
filesystem-free; root functions remain compatibility aliases.

Source Coverage is a third, single-part Audit core. Its registry/feed
aggregation, ordering, conservation, dominance, and missing-registry proof
belongs under `mechanics/audit/parts/source-coverage/tests/`. Boundary Bridge
may test how catalog and coverage signals return consumers to stronger owners,
but it must not become the test owner for Source Coverage producer behavior.

Receipt ABI Crossing owns the deterministic intake seam shared by every
receipt-backed projection. Envelope admission, JSON/JSONL loading, latest-event
deduplication, and conservative supersedes-family resolution are implemented
under `src/aoa_stats_builder/receipt_abi.py` and proved under the Boundary
Bridge part. The root build facade keeps compatibility aliases and tests only
their repo-wide fan-out effect; it is not the behavioral proof home for intake.

The Audit extraction preserves its historical ordered-input behavior and
compatibility buckets. Do not describe those retained mechanics as canonical
event chronology or owner activation truth. Changing them is a separate
behavioral cycle with public-output review, not part of a core extraction.

Route Progression is an RPG-owned projection boundary. The RPG center owns
progression-reading vocabulary and stop-lines; `aoa-skills` owns receipt
payloads, `aoa-agents` owns the agent-layer seven-axis overlay, and `aoa-sdk`
owns typed transport and consumer contracts. The current stats core projects
only the committed legacy numeric receipt shape. It must reject semantic-only
`axis_delta_summary` receipts rather than invent a score, and root builder
names remain compatibility aliases and fan-out only.

Route Progression consumer re-grounding must lead with the exact current
`aoa-skills` semantic receipt schema and example. The stats-local legacy
numeric fixture belongs to the reference input posture; it is not the first
stronger-owner return target.

Runtime Closeout is retired from active publication. The historical
`runtime_wave_closeout_receipt` remains admitted generic evidence for Object,
Repeated Window, and Source Coverage, but no current owner publishes that ABI
and no direct consumer requires its standalone projection. Keep the schema as
contract history and slot 22 as a cleanup tombstone; do not restore the
builder, catalog entry, or an empty repo-local Checkpoint package. The current
`abyss-stack` trial and `aoa-sdk` return receipt kinds remain distinct and must
not be silently aliased. Any future closeout surface needs a new reviewed
profile and slot plus an owner-approved ABI, real publisher, and evidence.

Repeated Window is a Recurrence-owned live projection boundary. Its authored
question and pure core may count admitted receipt activity by the calendar-date
prefix of `observed_at`; those buckets do not prove change, recurrence, cadence,
causality, or owner chronology. The root builder remains a thin compatibility
facade and fan-out route, including its historical object-identity hook.

Titan Incarnation is a committed-reference projection of the exact checked-in
`aoa-agents` operator/runtime rosters and `aoa-sdk` session-receipt example; its
core must reject cross-owner disagreement before deriving counts. Titan Summon
has no owner swarm-ledger instance and is retired from active publication. Its
source-home tombstone keeps the former output in managed stale cleanup without
keeping a builder, catalog entry, committed payload, or active mechanic claim.
A future observed Summon surface must enter through a new reviewed profile and
real owner-runtime plus refresh evidence rather than reviving zero defaults.

Owner Landing receipts remain admitted compatibility inputs for explicit
supersession and merge observations, but the standalone Owner Landing summary
is retired. No current owner publishes either accepted landing receipt kind,
and no current consumer requires the example-only aggregate. Keep the event
ABI and turnover normalization under Method Growth; do not keep a public
builder, generated payload, catalog entry, or empty owner-landing mechanic part
merely to replay the committed examples.

Read-model lifecycle has three source-owned states. `active/` authors public
catalog entries, `deferred/` authors contract-only candidates, and `retired/`
authors minimal cleanup/provenance tombstones. Retired records never enter the
public catalog or build fan-out. Their former output names remain in the live
cleanup universe until stale deployed copies are no longer a supported risk.
`catalog_order` is a stable slot identity, not a dense list position. Every
retired record reserves its `former_catalog_order`; active profiles may leave
gaps but must never reuse a retired slot or renumber simply because another
surface leaves publication. Former mechanic routes are provenance identifiers
and do not require an otherwise empty part to remain active.

Treat `live_state_capable` as an executable active-profile contract. The live refresh
mechanic may materialize and advertise only surfaces whose authored profile
sets it to `true`; it must still remove stale managed runtime files for
reference-only active surfaces and retired tombstones without silently
replaying fixtures or retired defaults as live state. Admission is not
provenance certification: audit the declared source posture of each `true`
profile separately.

Live admission requires both a current owner source and an observation route
that can cause refresh when that source changes. A builder that can resolve an
owner path on demand is not enough to keep continuously advertised local state
current. Memory Movement reads real reviewed `aoa-memo` corpus truth, but it
remains on the committed snapshot route until that corpus has an explicit
refresh trigger. Stress Recovery likewise remains out of live state until its
named owners publish real receipts and reports rather than only examples or
draft contracts. Owner Landing is retired rather than treated as a dormant
live candidate; any future standalone surface must enter through a newly
reviewed profile and real owner publisher.
Route Progression remains out of live state while its committed numeric
projection and the current owner-authored semantic receipt contract do not
share a non-invented projection ABI.

Antifragility Vector is the sole deferred read-model candidate. ATM10-Agent
already owns a real runtime publisher for one bounded stressor receipt, so the
candidate is not empty symmetry. It remains non-active because that receipt is
not registered for stats intake, adaptation deltas are schema/example only,
the bounded eval is draft/example only, and no repeated owner/eval window
demonstrates movement for the same stressor family. Its authored profile and
public deferred catalog entry must expose the exact `input_posture`,
`owner_truth_inputs`, `activation_gaps`, `consumer_risk`, and authority
ceiling. Do not add a builder, generated payload, live registration, or MCP
promotion until every gap closes and those publication contracts are reviewed
together.

For a profile-by-profile live-source audit, start at the owning mechanic
contract. Classify the current source chain as runtime/receipt-backed or
committed reference, make I/O and reference adaptation explicit, and only then
change the authored profile and source-home manifest to reflect that proven
mechanic boundary.

For Codex Plane Deployment, keep committed-reference and deploy-local modes
explicit. The committed build may project owner-authored examples; live refresh
may read only the named deploy-local rollout artifacts from its explicit
workspace root. Missing live artifacts omit the optional output and trigger
stale cleanup; they never authorize fallback to examples.

Keep Codex rollout history and cadence examples outside that deployment
boundary. The trusted-history mechanic reads the exact four checked-in
`8Dionysus/generated/codex/rollout/` owner surfaces. Campaign and drift-review
cadence projections read the separate three-example chain. Neither committed
context is live state, and neither may fall back to or impersonate the
deploy-local trio.

Trusted Rollout History also owns proof of its retained root compatibility
helper. The pure core requires the latest pointer to resolve inside history;
`scripts/build_views.py` alone preserves the older missing-pointer fallback
to the last row. Keep that exception explicit and part-tested beside the strict
core. It is not a source rule, and its focused test does not belong in the
repo-wide root suite.

## Cross-mode law

Grow `stats/` and `mechanics/` together, but alternate which side leads each
bounded slice:

1. name an evidenced mechanic route and its source-family crosswalk
2. add or tighten the corresponding stats source-family route
3. localize one coherent operation payload under the mechanic part
4. update the stats manifest only as needed to preserve the cross-contract
5. reverse the lead for the next slice

For every active family:

- one authored payload has one active owner home
- the stats route points to its mechanics route
- the mechanics route points back to its stats source family
- repo-local operation names are parts of a shared mechanic unless they prove
  a distinct repeatable owner boundary
- root wrappers survive only when they provide a real public or compatibility
  contract

Do not build either tree as an empty mirror of the other, and do not move
source meaning into mechanics merely because an operation touches it.

## AGENTS stack law

- Start with this root card, then follow the nearest nested `AGENTS.md` for
  every touched path.
- Root guidance owns repository identity, owner boundaries, route choice, and
  the shortest honest verification path.
- Nested guidance owns local contracts, local risk, exact files, and local
  checks.
- Authored sources own meaning. Generated, compact, exported, runtime, and
  adapter surfaces summarize, transport, or support it.
- Self-agency, recurrence, quest, progression, checkpoint, and growth language
  stays bounded, reviewable, evidence-linked, and reversible.
- Report what changed, what was verified, what was not verified, and where the
  next slice should resume.

## Memory route

For recall, continuity, compaction recovery, comparison with past work, or
preserved lessons, start with `aoa-memo` and the workspace memory map. Session
grounding routes through `.aoa`; local candidate writing routes through this
repository's `memo/` port when that port exists; durable reviewed memory lands
through `aoa-memo`.

## Decision review

After a meaningful structural, ownership, workflow, route-law,
validator-authority, derived-surface, public-contract, or topology change,
review whether future contributors need durable rationale in
`docs/decisions/`.

Do not create a decision record merely to duplicate a design surface or to
persist conversational context. If no decision record is needed, say so in
closeout.

## Derived-only rules

- Counts, windows, and movement summaries stay weaker than owner-local proof
  and source surfaces.
- Keep evidence references instead of duplicating raw artifacts when possible.
- Missing or stale source evidence remains visible; projection must not turn it
  into certainty.
- Builders and validators may enforce stats contracts, but cannot strengthen
  an upstream verdict.

## GitHub landing workflow

Root `AGENTS.md` owns the repository-wide branch, PR, CI, and merge route.
`.github/AGENTS.md` owns the GitHub-native files that support it.

When the user asks to commit, push, and merge in this repository:

1. Start from a branch based on current `origin/main`. If the worktree is
   already dirty, inventory it first and carry forward only the intended diff.
2. Commit the intended change with a message that names the changed surface.
3. Push the branch and open a pull request that states changed surfaces,
   validation run, skipped checks, and remaining risk.
4. Wait for GitHub `Repo Validation` and any required checks. Fix failures on
   the branch and wait for the replacement result.
5. Merge through GitHub after green validation. Use squash unless repository
   settings require another method, and report the method that landed.
6. Return to `main`, fast-forward from `origin/main`, and confirm the worktree
   is clean before closeout.

If GitHub status or merge permissions cannot be observed, stop the landing
route and report the exact blocker instead of guessing.

## Verify

Minimum repository validation:

```bash
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
python scripts/build_views.py --check
python scripts/validate_repo.py
python -m pytest -q tests mechanics
```

When mechanics or source-home topology changes, also run their focused
validators and tests:

```bash
python scripts/validate_mechanics_topology.py
python scripts/validate_stats_source_home.py
python scripts/validate_nested_agents.py --fail-on-untracked
python -m pytest -q tests/test_mechanics_topology.py tests/test_stats_source_home.py
```

When refresh behavior, watchers, or owner-local receipt intake changes:

```bash
python scripts/check_live_publishers.py
python scripts/refresh_live_stats.py
```

## Report

State which stats source family and mechanic route changed, whether output
shape or receipt registration changed, which owner repos supplied facts, what
compatibility surface remains, and what validation ran.

## Full reference

`docs/history/AGENTS_ROOT_REFERENCE.md` preserves the former detailed root
guidance as historical provenance. It is not an active instruction surface.
