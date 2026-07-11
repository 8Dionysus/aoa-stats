# aoa-stats mechanics

`mechanics/` is the operation home for repeatable work around authored stats
contracts. Use `stats/` to answer what a read model means; use this tree to
find which operation owns its payload, validation, and compatibility posture.

## Route

1. Read root `AGENTS.md` and `DESIGN.md`.
2. Find the authored family or surface profile under `stats/`.
3. Follow its `mechanic_routes` into the active part.
4. Read the package and part route cards.
5. Run the focused check plus the topology and source-home validators.

## Active packages

| Package | Local responsibility |
| --- | --- |
| `agon` | Agon prebinding and bounded observability registries |
| `antifragility` | vector, stress-recovery, and negative-evidence contracts |
| `audit` | coverage, object, skill-use, surface, and drift observations |
| `boundary-bridge` | receipt admission, consumer regrounding, and memory handoff |
| `checkpoint` | runtime closeout observation |
| `experience` | friction, adoption, governance, office, and release health contracts |
| `growth-cycle` | fork, session-growth, and automation follow-through summaries |
| `method-growth` | candidate lineage, owner landing, and supersession |
| `recurrence` | live refresh, component manifests, continuity, and repeated windows |
| `release-support` | deployment, rollout, campaign, and artifact-bundle support |
| `rpg` | multi-axis route progression |
| `titan` | incarnation, summon, runtime, and memory bridge observations |

`topology.json` is the machine-readable inventory. A sibling mechanic name is
not active here unless the topology names a real local operation.

## Placement law

- Operation-owned docs, fixtures, supporting schemas, manifests, scripts,
  units, and focused tests live under the nearest part.
- Stable catalog schemas and committed generated read models stay at their
  root public paths and are owned through `stats/read-models/` profiles.
- Root commands survive only as public, compatibility, or repo-wide
  entrypoints.
- Historical receipts live under package-local `legacy/`; they never become
  the first active route.
- The mechanics root contains only `AGENTS.md`, `README.md`, `topology.json`,
  and active package directories.
