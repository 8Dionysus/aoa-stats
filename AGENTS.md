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
15. the nearest nested `AGENTS.md` for every path you touch
16. `docs/history/AGENTS_ROOT_REFERENCE.md` only when historical pre-refactor
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

When several parts of one mechanic share deterministic receipt-to-read-model
rules, keep that reusable core under `src/aoa_stats_builder/`, declare its
focused package-level tests in `mechanics/topology.json`, and leave CLI, input
loading, output fan-out, and check/write policy in the root build facade.

Treat `live_state_capable` as an executable profile contract. The live refresh
mechanic may materialize and advertise only surfaces whose authored profile
sets it to `true`; it must still remove stale managed runtime files for
reference-only surfaces without silently replaying their fixtures as live
state. Admission is not provenance certification: audit the declared source
posture of each `true` profile separately.

Live admission requires both a current owner source and an observation route
that can cause refresh when that source changes. A builder that can resolve an
owner path on demand is not enough to keep continuously advertised local state
current. Memory Movement reads real reviewed `aoa-memo` corpus truth, but it
remains on the committed snapshot route until that corpus has an explicit
refresh trigger. Owner Landing and Stress Recovery likewise remain out of live
state until their named owners publish real receipts and reports rather than
only examples or draft contracts.

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
