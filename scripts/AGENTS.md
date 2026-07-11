# AGENTS.md
Local guidance for `scripts/` in `aoa-stats`.

Read the root `AGENTS.md` first. Root scripts are repo-wide commands or stable
compatibility entrypoints. Live refresh implementations belong to
`mechanics/recurrence/parts/live-receipt-refresh/scripts/`; summary-catalog
bundle validation belongs to its Release Support part.

## Local role
Scripts should be deterministic, repo-relative, and derived-only. Prefer check
mode for builders, especially `build_views.py --check`.

## Editing posture
Avoid hidden network calls, hidden writes, and time-dependent output. Neighbor
source discovery must use a deterministic, testable precedence and keep
explicit environment overrides first. When live refresh behavior changes,
keep dry-run or explicit operator intent visible.

## Hard no
Do not let a script infer owner truth from volume. Do not make refresh behavior
silently mutate source repos.

## Validation
Run the touched script, then:

```bash
python scripts/validate_mechanics_topology.py
python scripts/validate_stats_source_home.py
python scripts/validate_repo.py
python -m pytest -q tests mechanics
```
