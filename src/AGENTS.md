# AGENTS.md
Local guidance for `src/` in `aoa-stats`.

Read the root `AGENTS.md` before changing package code. Builder changes also
start from the selected profile under `stats/read-models/` and its mechanic
contract; MCP changes start from `stats/surface-catalog/CODEX_MCP.md`.

## Local role
`src/aoa_stats_builder/` owns deterministic projection core and
`src/aoa_stats_mcp/` owns read-only access implementation. Root scripts own
repo-wide orchestration and compatibility entrypoints. Source code should make
stats surfaces easier to build or read without claiming workflow, proof,
route, or quest authority.

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
python -m pytest -q tests/test_aoa_stats_mcp_state.py
python scripts/validate_repo.py
```
