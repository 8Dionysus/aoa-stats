# AGENTS.md

## Agon agent guide

This package owns the `aoa-stats` implementation of the common
`Agents-of-Abyss/mechanics/agon` mechanic. When an Agon operation is selected,
follow the package README, `PARTS.md`, provenance, and the part named by
`mechanics/topology.json`.

## Active payload law

- Active source payload belongs below `parts/<part>/`.
- A part keeps config, docs, examples, schemas, builders, validators, and
  focused tests together.
- The root-published `generated/agon_*.min.json` compatibility outputs are
  built from part-local sources and retain their stable paths.
- Stable schema identities are contract identities; relocation alone is not a
  reason to rewrite them.
- Agon recurrence declarations remain with the recurrence component-manifests
  part; they are cross-routed integration surfaces, not duplicate payload.

## Boundary and legacy law

Agon observability is candidate-only. It must not open an arena, issue a
verdict, write a scar, execute retention, mutate rank or trust, promote to KAG
or Tree of Sophia, schedule hidden work, or make the assistant a contestant.

Historical landing notes and closed quests are represented by
`PROVENANCE.md` and `former-routes.json`; they are evidence of how active parts
arrived, not instructions. Recover retired source only from the exact baseline
Git tree pinned by AOST-D-0024. No local `legacy/` archive is an active route.

## Conditional validation and closeout

Use the nearest Agon part `VALIDATION.md` and report builder/validator results,
generated paths, candidate posture, and any owner or runtime evidence not
established. A local check does not prove arena, verdict, promotion, or owner
acceptance.
