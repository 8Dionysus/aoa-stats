# AGENTS.md
Local guidance for `scripts/` in `aoa-stats`.

Read the root `AGENTS.md` first. Scripts here build derived views, validate
receipt ABI, refresh live stats, inspect publishers, and serve repo-local MCP.

## Local role
Scripts should be deterministic, repo-relative, and derived-only. Prefer check
mode for builders, especially `build_views.py --check`.

## Editing posture
Avoid hidden network calls, hidden writes, time-dependent output, and implicit
source discovery. When live refresh behavior changes, keep dry-run or explicit
operator intent visible.

## Hard no
Do not let a script infer owner truth from volume. Do not make refresh behavior
silently mutate source repos.

## Validation
Run the touched script, then:

```bash
python scripts/validate_repo.py
python -m pytest -q tests
```
