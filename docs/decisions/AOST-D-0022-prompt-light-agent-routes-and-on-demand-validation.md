# AOST-D-0022 Prompt-Light Agent Routes And On-Demand Validation

## Index Metadata

- Decision ID: AOST-D-0022
- Original date: 2026-08-31
- Surface classes: agent guidance, validation, docs route, public contract
- Stats surfaces: root route, local agent mesh, owner-local validation, derived observability
- Source lanes: stats source home, mechanics topology, owner-local validators
- Guard families: prompt visibility, owner authority, derived-only authority, source coverage, validation completeness
- Posture: accepted prompt-light route law; no measurement, validation-sufficiency, runtime, or release-admission change

## Context

The `aoa-stats` agent mesh carries essential measurement, missingness,
uncertainty, provenance, lifecycle, derived-only, and stronger-owner limits. It
also places full command batteries and branch/PR/CI/merge procedure in inherited
`AGENTS.md` cards, while the root card requires a broad README and design
inventory before the touched statistical surface is known.

The stronger owners already exist. `stats/source_home.manifest.json` owns the
stats-family crosswalk, `mechanics/topology.json` owns operation placement,
part `VALIDATION.md` files own focused human procedure, and
`scripts/release_check.py` owns the complete ordered repository gate. Under
`AOST-D-0019`, validation telemetry remains a derived measurement extension;
`aoa-stats` must not turn its observability role into a central validation graph
or sufficiency authority for sibling owners.

The task is therefore to reduce inherited procedure without reducing
statistical meaning, owner-local validation, human navigation, or evidence
ceilings.

## Decision

Use root and nested `AGENTS.md` as prompt-light semantic route cards. They own
applicable scope, local role, measurement and operation ownership, source and
stronger-owner routes, missingness/provenance/lifecycle limits, generated and
runtime stop-lines, impact-based validation selection, and closeout claims.
They must not duplicate runnable command batteries, complete inspection
transcripts, a general package overview, or the full GitHub landing procedure.

Add root `VALIDATION.md` as the on-demand human entrypoint for focused checks,
the full repository gate, generated parity, source-home and topology checks,
live-refresh conditions, checkpoint review, and ordinary landing procedure.
Keep exact part-local procedure in the nearest `VALIDATION.md`. Route cards
name the applicable validation surface or evidence class only when the touched
path and risk require it.

The procedure layer is not machine authority. `scripts/release_check.py` and
its ordered `COMMANDS` remain the owner-local complete gate. Authored stats
families and `stats/source_home.manifest.json` own statistical membership;
`mechanics/topology.json` owns operation and focused-proof placement. Neither
root `VALIDATION.md` nor validation telemetry may invent a sibling claim set,
sufficiency verdict, or central graph.

Add `DESIGN.AGENTS.md` as an on-demand design surface for the root-to-local
agent mesh, conditional reading, README role, validation split, and source
hierarchy. It is not an inherited route card and does not replace `DESIGN.md`,
active owner sources, manifests, topology, validators, or decisions.

Keep root `README.md` as the public human entrypoint. Keep local README files
when they explain a stats family, mechanic, operation, usage path, contract, or
archive boundary. README is task-conditional agent reading and never becomes
statistical source authority by filename. Removing or consolidating a README
requires separate owner-aware evidence for human function, inbound links,
manifest/topology requirements, generator relationships, fixtures, and
consumers; this decision authorizes no blanket deletion.

Move ordinary branch, PR, required-check, merge-method, and post-landing
procedure to `docs/RELEASING.md` or root `VALIDATION.md`. Root `AGENTS.md`
retains only the landing route, evidence boundary, and fail-closed stop-line
when status or authority is unavailable.

Generated decision indexes, public read models, KAG families, stats catalogs,
and other projections remain derived. Change authored sources or builders
first and regenerate; do not hand-edit a projection while changing routes.

## Options Considered

- Keep commands in inherited cards and optimize only their prose.
- Move commands and owner doctrine into README files.
- Centralize all owner validation claims in `aoa-stats` because it already
  measures validation telemetry.
- Keep inherited cards semantic, expose procedure on demand, preserve existing
  owner-local machine authorities, and retain README according to human value.

## Rationale

Measurement identity, missingness, provenance, derived-only limits, and owner
return affect the meaning of every action and belong in inherited context.
Exact procedure matters after a surface and risk have been selected. Keeping
those layers separate lowers prompt pressure while making the command owner
more explicit.

An on-demand agent-design surface lets future contributors evolve the mesh
without expanding root guidance. Refusing a central graph preserves the
existing stats boundary: measurement may make validation behavior comparable,
but it cannot decide whether another owner has proved enough.

## Consequences

- Inherited agent context becomes smaller and task-conditional.
- Human procedures remain discoverable through one root route and nearest part
  validation surfaces.
- Validators must reject runnable procedure and unconditional README inventories
  in active `AGENTS.md` while retaining complete card/topology coverage and
  owner-boundary checks.
- Existing tests that treat `AGENTS.md` as a command owner must move that
  expectation to `VALIDATION.md`, `scripts/release_check.py`, or a named
  operator guide without weakening the full gate.
- README disposition stays per-file and evidence-based.
- Validation telemetry, generated summaries, local green checks, CI execution,
  review, and merge remain distinct evidence classes.

## Source Surfaces

- `AGENTS.md`
- `DESIGN.md`
- `DESIGN.AGENTS.md`
- `README.md`
- `VALIDATION.md`
- `docs/RELEASING.md`
- `scripts/release_check.py`
- `scripts/validate_nested_agents.py`
- `stats/source_home.manifest.json`
- `mechanics/topology.json`
- `mechanics/*/parts/*/VALIDATION.md`
- `tests/test_docs_routes.py`
- `docs/decisions/AOST-D-0019-owner-safe-validation-telemetry.md`

## Validation

Run decision-index parity, nested-agent and documentation route checks,
source-home and mechanics topology validators, focused validation-owner tests,
generated parity, and the full repository gate through root `VALIDATION.md`.
No generated or telemetry surface is acceptance evidence by itself.
