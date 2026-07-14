# AGENTS.md

Root route card for `aoa-stats`.

## Purpose

`aoa-stats` is the central statistical measurability organ of OS Abyss. It
defines a shared measurement grammar and federates owner-local `stats/` ports,
then consumes source-owned receipts, evidence references, and bounded verdicts
to build deterministic read models without taking authority from their owners.

Dashboards are lanterns, not sovereigns.

## Owner lane

This repository owns:

- the shared grammar for measurement identity, populations, units,
  dimensions, aggregation, missingness, uncertainty, provenance, lifecycle,
  reporting rules, privacy, and live/reference posture
- the compatible root `stats/` port contract and owner coverage inventory
- the stable meaning and contracts of stats-authored read models
- one bounded question and authority ceiling for each non-catalog stats
  operation contract
- the shared receipt envelope and event-kind vocabulary used by those models
- deterministic projection, refresh, validation, and derived-only access

Owner repositories own their questions, metric definitions, populations,
dimensions, evidence handoffs, privacy posture, and exports. This repository
does not own workflow, proof, practice, scenario, role, memory, KAG, runtime,
route, quest-state, RPG meaning, or self-agent truth. Counts do not create
mastery, intent, causality, or owner truth.

## Start here

1. `README.md`
2. `DESIGN.md`
3. `stats/README.md` for the source-authored stats home
4. `mechanics/README.md` for repeatable operation topology
5. `ROADMAP.md`
6. `docs/BOUNDARIES.md`
7. `docs/ARCHITECTURE.md`
8. `docs/decisions/README.md` for durable rationale and generated lookup
9. the nearest nested `AGENTS.md` for every path you touch
10. `docs/history/AGENTS_ROOT_REFERENCE.md` only for historical provenance

Do not turn this root card into a profile-by-profile status roster. Exact
surface state belongs in `stats/read-models/`; non-catalog input maturity
belongs in `stats/operation-contracts/`; operation detail belongs in the
owning mechanic part; rationale belongs in `docs/decisions/`.

Apply the same rule to public entrypoints. Root `README.md` and
`docs/ARCHITECTURE.md` may explain stable routes and derived-view structure,
but must not duplicate changing profile counts, named lifecycle rosters, or a
part-by-part operation map.

`ROADMAP.md` owns direction, priority, and cross-slice sequencing. It routes
exact current state to profiles, topology, generated discovery, decisions, and
history instead of replaying surface rosters, live/retired counts, mechanic
payload lists, or compatibility chronology.

Mechanic contracts and operator guides own stable selection, refresh, cleanup,
and failure rules. They derive exact profile membership and counts from the
authored source records at validation or runtime; they do not freeze a complete
live/reference/retired roster in prose. Keep a named exception only when a
focused operation boundary needs it, and route its current posture back to the
profile and indexed decision.

## Repository contract

`aoa-stats` has two cross-routed active homes:

- `stats/` owns source-authored stats meaning, lifecycle, authority ceilings,
  and source-family routes.
- `mechanics/` owns repeatable intake, projection, refresh, validation, and
  release operations around those sources.

`stats/source_home.manifest.json` is the machine-readable source-family
crosswalk. `mechanics/topology.json` is the machine-readable operation and
placement map. Human route docs explain those maps; they do not override them.

The `measurement_contract` family owns portable statistical shape. The
`federation` family owns local-port compatibility and the durable owner-level
coverage inventory. Neither may copy owner-local definitions or one-session
workspace state.

Repo-wide validators keep only stable repository entrypoints as their direct
text inventory. Stats-family membership comes from the source manifest and
mechanic membership from topology and part validation; do not copy selected
family or part docs into a root validator constant.

Apply the same rule to mechanic package membership. The topology activation
map, active package records, and materialized root directories must agree;
tests and route docs do not carry a second fixed package roster as machine
truth.

Operation payload lives under the nearest mechanic part. Root `schemas/` and
`generated/` remain stable public districts. Root `scripts/` and `tests/`
keep only public, compatibility, or repo-wide surfaces. Other root districts
need an explicit public, decision, bundle, or compatibility role declared by
topology and validated by the repository gates.

A stable root module does not make every historical helper name permanent ABI.
Retain a symbol-level compatibility export only for a current caller, explicit
external contract, or focused owner-part proof. Put reusable deterministic
logic under `src/aoa_stats_builder/`; keep I/O, CLI, fan-out, and check/write
policy at the edge. Part-specific behavior is proved by its part, while a
package-level test district requires a genuinely shared core and an explicit
`package_payload_roots` declaration.

Source-family proof routing follows topology rather than a named part roster.
When a part declares a localized `tests/` payload, family-level validation
checks that the district contains focused proof and routes at least one current
test without copying current part names into root proof.

Apply the same evidence test to relocated owner references. Re-ground current
authored consumers and fixtures on the canonical owner path before removing a
translation alias; once no current consumer requires it, the exact source
adapter must not preserve a hidden fallback merely because the surface remains
reference-only. Reference posture limits publication authority, not source-ref
precision.

A root documentation redirect follows the same evidence test. Retain it only
for a current public consumer or explicit external contract. Once active
readers point to the part-local owner, remove the redirect from topology and
validation; Git history and provenance bridges preserve the former path.

Cross-owner caution and precedence guidance is operation payload when one
mechanic applies it. Keep that guidance with the mechanic part that returns
consumers to stronger owners; do not retain a root doc merely because its rule
mentions several organs.

Stats-authored vocabulary that constrains profile meaning belongs to the
matching family under `stats/`. Root `docs/` may explain repository-wide
architecture and boundaries, but it must route to the source owner instead of
retaining a second vocabulary entrypoint or current profile status.

## Cross-mode law

Grow `stats/` and `mechanics/` together, alternating which side leads each
bounded slice:

1. identify the source-owned fact, current payload owner, and consumer
2. strengthen one stats family or one evidenced mechanic part
3. update only the reciprocal route needed on the other side
4. localize focused payload and proof under the operation owner
5. validate the crosswalk in both directions
6. reverse the lead for the next slice

One authored payload has one active owner. Do not build empty mirror packages,
move source meaning into mechanics, or preserve root wrappers without a real
public or compatibility contract.

## Lifecycle and authority

- `active/` read-model profiles author public catalog surfaces.
- `deferred/` profiles author evidence-gated contract candidates, not future
  promises or hidden activation.
- `retired/` profiles are cleanup/provenance tombstones. They publish no
  surface and reserve their former catalog slots.
- `live_state_capable` is executable source meaning. Live materialization
  requires both a current owner source and an observation route that notices
  movement; the selector alone does not certify provenance.
- Reintroducing a retired question requires a new reviewed active profile,
  current owner evidence, a producer, a new reviewed slot, and validation.
- Operation bindings must state whether inputs are current, reference-only, or
  symbolic. Documentation and examples do not become runtime evidence.
- Generated, compact, MCP, adapter, and runtime convenience surfaces remain
  weaker than authored profiles and owner-local facts.
- The stack-owned `aoa-stats-mcp` is the only MCP access implementation.
  `aoa-stats` owns its transport-neutral read contract; `abyss-stack` owns
  runtime transport and lifecycle. Do not reintroduce a repo-local server or
  move statistical semantics into the access plane.

For any specific surface, follow its profile or operation record, mechanic
contract, focused validation card, and indexed decision rationale. Do not copy
its changing status back into this root card.

Source validators derive lifecycle membership from authored directories and
catalog projection rather than fixed profile counts. They derive non-catalog
operation membership from authored records and the reciprocal mechanics
crosswalk rather than a fixed part count. Stable catalog slots and retired
reservations remain intentional public identity guards; cardinality is not an
ABI by itself.

## AGENTS stack law

- Root guidance owns repository identity, route choice, owner boundaries, and
  the shortest honest verification path.
- Nested guidance owns local contracts, local risk, exact files, and focused
  checks.
- Authored sources own meaning. Generated and access surfaces summarize,
  transport, or support it.
- Report what changed, what was verified, what was not verified, and where the
  next cross-slice should resume.

## Memory and decision routes

For recall, compaction recovery, or past-session evidence, start with
`aoa-memo` and the workspace memory route; `.aoa` evidence can rehydrate
context but cannot override repository sources.

After a meaningful structural, ownership, workflow, route-law, validator,
public-contract, or topology change, check the decision graph and
`docs/decisions/`. Do not create a decision merely to duplicate design prose
or conversational context.

## Derived-only rules

- Counts, windows, and movement summaries stay weaker than owner-local proof.
- Prefer evidence references over copies of owner artifacts.
- Missing, stale, rejected, or unregistered evidence remains visible.
- Builders and validators may enforce stats contracts but cannot strengthen an
  upstream verdict.

## GitHub landing workflow

Root `AGENTS.md` owns the repository-wide branch, PR, CI, and merge route.
`.github/AGENTS.md` owns the GitHub-native files that support it.

When the user asks to commit, push, and merge:

1. Start from current `origin/main`; inventory a dirty worktree before
   carrying only the intended diff.
2. Commit with a message naming the changed surface.
3. Push and open a PR stating changed surfaces, validation, skipped checks, and
   remaining risk.
4. Wait for `Repo Validation` and every required check; repair failures on
   the branch and wait for the replacement result.
5. Merge through GitHub after green validation, using squash unless repository
   settings require another method.
6. Verify the resulting `main` push check, then validate a clean post-merge
   worktree before closeout.

If GitHub status or merge permission cannot be observed, report the exact
blocker instead of guessing.

## Verify

Minimum full gate:

```bash
python scripts/release_check.py
```

For source-home, mechanics, or route-card changes, also run:

```bash
python scripts/validate_stats_source_home.py
python scripts/validate_stats_protocol.py
python scripts/validate_mechanics_topology.py
python scripts/validate_nested_agents.py --fail-on-untracked
python -m pytest -q tests/test_stats_source_home.py tests/test_mechanics_topology.py tests/test_docs_routes.py
```

Run the touched part's `VALIDATION.md` before the full gate. Refresh behavior
changes also require the live-publisher and live-refresh checks.

## Report

State which stats source family and mechanic route changed, whether output
shape or receipt registration changed, which owner repos supplied facts, what
compatibility surface remains, and what validation ran.

## Historical reference

`docs/history/AGENTS_ROOT_REFERENCE.md` preserves pre-refactor guidance as
provenance. It is not an active instruction surface.
