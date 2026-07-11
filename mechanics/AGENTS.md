# AGENTS.md

## Mechanics agent guide

Read the repository root `AGENTS.md` and `DESIGN.md` first. Then use
`stats/source_home.manifest.json`, the selected read-model profile, and
`mechanics/topology.json` to choose the active package and part.

## Edit law

- Keep source meaning and authority ceilings in `stats/`.
- Keep repeatable operation payload under the nearest mechanic part.
- Keep `src/` importable code separate from operation routing.
- Retain a root schema, generated output, command, doc, or fixture only when
  the topology declares its public, compatibility, or repo-wide role.
- Do not duplicate an active payload at an old root path.
- Keep package-local legacy behind `PROVENANCE.md` and an explicit legacy
  index; raw history is never active law.
- Do not add a package or part for visual symmetry alone. It needs a real
  payload or declared public surface and focused validation.

## Cross-contract

Every active profile under `stats/read-models/` names one or more existing
mechanic parts. Each active part must own localized payload, a declared public
surface, compatibility route, or package-local historical accounting. The
topology validator checks both directions and the root exception set.

## Validation

```bash
python scripts/validate_mechanics_topology.py
python scripts/validate_stats_source_home.py
python -m pytest -q tests/test_mechanics_topology.py tests/test_stats_source_home.py
```
