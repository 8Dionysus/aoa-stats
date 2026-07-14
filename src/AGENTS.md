# AGENTS.md
Local guidance for `src/` in `aoa-stats`.

Read the root `AGENTS.md` before changing package code. Measurement-core
changes start from `stats/measurement-contract/` and its Boundary Bridge part.
Derived-view changes start from the selected profile under
`stats/read-models/` and its mechanic contract. Public stats-access semantics
start from `stats/surface-catalog/CODEX_MCP.md`; runnable MCP changes belong to
the stack-owned `aoa-stats-mcp` service.

## Local role
`src/aoa_stats_builder/` contains pure executable interpretations of
stats-authored contracts plus bounded derived-view code and adapters.
Root scripts own repo-wide orchestration and compatibility entrypoints. Source
code should make stats surfaces easier to build or read without claiming
workflow, proof, route, or quest authority. MCP transport and service lifecycle
are outside this repository.

## Editing posture
Keep projection logic free of filesystem and environment policy when it can be
expressed as a deterministic input-to-read-model mapping. Keep APIs small,
typed where practical, and explicit about boundary rules. For access code,
start with catalog-style access, then preview, then full reads only when needed.

## Hard no
Do not add write actions, raw receipt tailing, route mutation, proof verdicting,
or source-repo control from this package.

## Validation
Run:

```bash
python -m pytest -q mechanics tests
python scripts/build_views.py --check
python scripts/validate_repo.py
```
