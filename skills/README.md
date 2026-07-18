# aoa-stats Skill Home

This directory is the canonical home for callable procedures owned specifically
by `aoa-stats`. It is not a mirror of the shared AoA catalog.

## Admitted bundle

| Bundle | Internal modes | Visibility | Admission |
| --- | --- | --- | --- |
| `aoa-stats` | `answer`, `diagnose`, `evolve` | OS-user-advertised | `docs/decisions/AOST-D-0013-aoa-stats-owner-skill-bundle.md` |

The three modes share one trigger family, authority ladder, result ABI, and
coexistence boundary. They remain one bundle until held-out manual work proves
that separate prompt-visible procedures improve outcomes.

`port.manifest.json` declares admitted source and selection by the single
OS-level `os-user-default` profile. Canonical files live under
`skills/aoa-stats/`; this repository does not duplicate the globally installed
bundle under `.agents/skills`.

## Verification posture

Manual tasks establish usefulness. Working validation commands live in
`skills/AGENTS.md`. The pinned `aoa-skills` source check validates identity,
admission, and package digest; the OS profile installer separately previews
collisions and verifies the managed user copy. Neither check proves routing,
model portability, safety, or outcome benefit.
