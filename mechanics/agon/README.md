# Agon mechanic

`mechanics/agon/` is the local `aoa-stats` implementation of the common
`Agents-of-Abyss/mechanics/agon` mechanic.

It turns owner-retained Agon observations into bounded, schema-backed,
candidate-only stats surfaces. It does not inherit Agon runtime or judgment
authority.

## Active shape

Eight operation parts are active and their 68 source payload files are
part-local. Two cross-part boundary documents live in `docs/`.

The eight generated registries intentionally remain under root `generated/`
as public compatibility outputs. This publication exception does not move
their source ownership back to the root districts.

## Route

Start with `PARTS.md`, then read the selected part's `README.md`, `CONTRACT.md`,
and `VALIDATION.md`. Use `PROVENANCE.md` for the active-first history and
`legacy/INDEX.md` for former landing and quest routes.
