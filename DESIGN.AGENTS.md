# aoa-stats Agent Surface Design

## Role

This document owns the desired form of agent-facing guidance in `aoa-stats`.
It is read on demand when card placement, conditional reading, validation
routing, or closeout shape changes. It is not an `AGENTS.md` card and does not
override `DESIGN.md`, authored stats sources, mechanics topology, schemas,
builders, validators, or decisions.

## Thesis

The agent layer is a route mesh, not a statistical encyclopedia:

- root `AGENTS.md` names repository identity, owner boundaries, global
  evidence limits, route choice, and closeout;
- the nearest nested card adds only the local semantic delta;
- authored stats records and owner-local sources own meaning;
- manifests and topology own machine membership and placement;
- `VALIDATION.md` exposes executable human procedure on demand;
- `scripts/release_check.py` owns the complete repository gate;
- generated read models support navigation and observation without gaining
  source or sufficiency authority.

The root names the measurement road. The nearest card narrows the question.
The source owns meaning. The mechanic owns the operation. The validator checks
the crossing. The closeout returns stronger claims to their owner.

## Reading Shape

For ordinary work, inherit root `AGENTS.md`, then read the nearest nested card
for every touched path. Open only the source family, operation record,
mechanic part, schema, builder, test, or owner contract needed by the current
question.

Read `README.md` when public or human orientation is needed. Read `DESIGN.md`
when repository or source/mechanics form changes. Read this document when the
agent mesh itself changes. Read the nearest `VALIDATION.md` when execution or
proof selection begins. Entering a directory alone does not require its whole
README/design inventory.

## Card Law

An active `AGENTS.md` may carry:

- applicable scope and role;
- the local source and stronger-owner route;
- measurement, population, missingness, uncertainty, privacy, provenance, and
  lifecycle invariants relevant to that district;
- authored/generated, reference/live, proof/measurement, and source/runtime
  stop-lines;
- the name or link of the focused validation route;
- closeout evidence and owner return.

It should not carry runnable command blocks, complete validation matrices,
branch/PR/CI/merge recipes, mutable profile or part rosters, generic package
explanation, or inherited prose already supplied by a parent card.

Local cards exist where a durable owner boundary, risk, source choice, or
validation choice changes. They do not need to mirror every directory.

## Authority Split

| Concern | Owner |
| --- | --- |
| shared measurement and read-model meaning | authored records under `stats/` |
| owner-local metric meaning | the owner repository's stats port and sources |
| operation placement and focused proof | `mechanics/topology.json` and the nearest part |
| human validation procedure | root or nearest part `VALIDATION.md` |
| complete owner-local repository gate | `scripts/release_check.py` |
| durable rationale | `docs/decisions/` |
| public and human explanation | `README.md` and public docs |
| derived navigation and observation | generated stats and KAG read models |

Validation telemetry measures owner-declared execution and evidence posture.
It does not own another repository's validator, claim set, sufficiency, or
landing decision.

## README And Generated Surfaces

Root README remains the public front door. A local README remains when it
provides a human family atlas, mechanic role, usage path, contract explanation,
or archive boundary. It is not mandatory agent context unless the current task
needs that function.

Generated files are changed through their authored inputs and canonical
builders. Compact catalogs, counts, KAG projections, MCP responses, runtime
caches, and dashboards stay weaker than their sources and receipts.

## Stop-Lines

Agent guidance must not:

- let a count, trend, coverage ratio, or green command imply proof, causality,
  mastery, health, or owner acceptance;
- absorb owner-local questions or metric definitions into the central organ;
- turn validation telemetry into a central validation graph;
- hide missing, stale, rejected, unregistered, or reference-only evidence;
- make generated, MCP, KAG, cache, or dashboard surfaces source truth;
- place live state or private evidence in committed guidance;
- preserve a command in inherited context merely because it once lived there.

## Closeout

State the stats family and mechanic route changed, source and generated
surfaces affected, owner inputs used, validation actually run, missing or
skipped evidence, whether any claim moved toward live or public posture, and
the next owner route. Local validation is not CI, review, merge, or post-merge
acceptance.
