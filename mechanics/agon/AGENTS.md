# AGENTS.md

## Agon agent guide

This package owns the `aoa-stats` implementation of the common
`Agents-of-Abyss/mechanics/agon` mechanic. Read `../AGENTS.md`, `README.md`,
`PARTS.md`, and `PROVENANCE.md` before editing a part.

## Active payload law

- Active source payload belongs below `parts/<part>/`.
- A part keeps its config, docs, examples, schemas, builders, validators, and
  focused tests together.
- The eight `generated/agon_*.min.json` files remain root-published public
  outputs. Their builders must read part-local sources and write those exact
  compatibility routes.
- Stable schema identities are contract identities; relocation alone is not a
  reason to rewrite them.
- `mechanics/recurrence/parts/component-manifests/` owns the recurrence
  declarations and Agon recurrence review boundary. They are cross-routed
  integration surfaces, not duplicate Agon payload.

## Boundary

This package derives candidate-only observability. It must not open an arena,
issue a verdict, write a scar, execute retention, mutate rank or trust, promote
to KAG or Tree of Sophia, schedule hidden work, or make the assistant a
contestant.

## Legacy law

Historical landing notes and closed quests live under `legacy/raw/`. They are
evidence of how the active parts arrived, not active instructions. Route
through `legacy/INDEX.md` and `legacy/former-routes.json` instead of linking to
raw history as current guidance.

## Validation

Run the builder check, validator, and focused pytest command recorded in the
touched part's `VALIDATION.md`. Do not validate a moved builder through its
former root script route.
