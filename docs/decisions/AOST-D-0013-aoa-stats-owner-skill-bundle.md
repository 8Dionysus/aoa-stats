# AOST-D-0013 aoa-stats Owner Skill Bundle

## Index Metadata

- Decision ID: AOST-D-0013
- Original date: 2026-07-15
- Surface classes: skills/home, agent interface, repository projection, owner boundary
- Stats surfaces: measurement contract, federation, intake, read models, live refresh, source coverage, access
- Source lanes: aoa-stats owner sources, owner-local stats ports, bounded proof, runtime observation
- Guard families: derived-only authority, manual admission, source/projection parity, negative applicability
- Posture: accepted

## Status

Accepted

## Context

The repository exposed 25 copied shared bundles under `.agents/skills` but had
no canonical home for its own callable procedure. Those copies competed with
the shared user profile, carried obsolete skill names, and could not express
the stats-specific authority ladder. A prior prototype proposed several narrow
visible skills, but their triggers, result shape, and owner boundaries largely
overlapped.

Manual work exercised a bounded owner-inventory answer, a stale live-publisher
diagnosis, a proposed global freshness score, retired-lifecycle and
committed-versus-live held-out cases, a newly missing owner-catalog metric, and
negative/coexistence requests. The procedure repeatedly prevented counts,
parseability, systemd success, or generated freshness from becoming owner
health. It also returned the global score proposal to owner-local freshness
meaning and disconfirmed the service layer before naming an upstream receipt
boundary.

## Decision

Admit one repository-owned `aoa-stats` bundle with internal `answer`,
`diagnose`, and `evolve` modes. Its canonical source lives at
`skills/aoa-stats/SKILL.md`; `skills/port.manifest.json` declares version and
admission. The exact repo-scoped Codex copy is generated at
`.agents/skills/aoa-stats` through the common `aoa-skills` home-port contract.

Remove the 25 undeclared shared copies from the repository projection. Do not
split the three modes into separate prompt-visible bundles unless later
held-out trials establish independent triggers, ABIs, composition value, and
outcome benefit.

Remove the root test that imported `bringup_contract.py` from the copied
`aoa-local-stack-bringup` projection. The tested behavior belongs to a target
runtime owner's stack workflow, not to `aoa-stats`; retaining the test would
make a generated foreign projection a hidden source and release dependency.

## Options Considered

- Keep the copied shared catalog and rely on generic procedures: preserves no
  source migration, but retains routing interference and no stats owner ABI.
- Advertise a separate skill for each stats operation or internal mode: makes
  names explicit, but multiplies semantically adjacent candidates before
  independent benefit is demonstrated.
- Admit one owner bundle with three internal modes and one exact derived
  projection: preserves a small discovery footprint and one authority chain.
- Keep no skill and rely only on root guidance: avoids prompt cost, but manual
  comparisons showed repeated value from the bounded result ABI, negative
  applicability, adjacent-layer disconfirmation, and explicit no-change route.

## Rationale

The three modes select different actions but share applicability, owner
sources, authority ordering, output fields, failure vocabulary, and collision
boundaries. One bundle is the smallest callable unit supported by the observed
work. The repository owns its adaptation; `aoa-skills` owns only the common
projection grammar, and KAG remains a source-linked retrieval layer.

Raw trials and task-local DAGs stay in the session. The durable record keeps
only the admission rationale and claim limits.

## Consequences

- Codex sees one stats-specific repository skill instead of 25 copied shared
  names.
- The repository gate no longer claims ownership of a retired portable
  local-stack helper through a copied projection.
- Answer and diagnosis remain read-only; source mutation requires explicit
  `evolve` authority.
- Generic analytics, eval-verdict interpretation, routing, workflows, runtime
  repair, and already-named validator execution remain negative cases.
- Structural validation can prove owner and byte parity but cannot prove
  routing quality, cross-model transfer, safety, or outcome improvement.
- A material model, workflow, or bundle change requires new isolated,
  negative, held-out, and coexistence work before lifecycle expansion.

## Source Surfaces

- `AGENTS.md`
- `DESIGN.md`
- `docs/BOUNDARIES.md`
- `skills/AGENTS.md`
- `skills/README.md`
- `skills/aoa-stats/SKILL.md`
- `skills/port.manifest.json`
- `stats/source_home.manifest.json`
- `mechanics/topology.json`
- `aoa-skills:docs/decisions/AOA-SK-D-0040-owner-skill-homes-and-projection-boundaries.md`
- `aoa-skills:docs/decisions/AOA-SK-D-0041-minimal-owner-home-port-contract.md`

## Validation

Decision indexes, portable `SKILL.md` validation, the pinned common home-port
action, prompt-visible fresh-session inspection, repo-local KAG parity, and the
root release gate protect the durable shape. Manual trials remain the semantic
admission evidence; green checks do not replace them.
