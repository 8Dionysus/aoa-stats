# AGENTS.md
Local guidance for `src/` in `aoa-stats`.

Read the root `AGENTS.md` and `docs/CODEX_MCP.md` before changing package code.

## Local role
Source code may expose derived-only helpers such as `aoa_stats_mcp`. It should
make stats surfaces easier to read without claiming workflow, proof, route, or
quest authority.

## Editing posture
Start with catalog-style access, then preview, then full reads only when needed.
Keep APIs small, typed where practical, and explicit about boundary rules.

## Hard no
Do not add write actions, raw receipt tailing, route mutation, proof verdicting,
or source-repo control from this package.

## Validation
Run:

```bash
python -m pytest -q tests/test_aoa_stats_mcp_state.py
python scripts/validate_repo.py
```
