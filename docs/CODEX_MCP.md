# Codex MCP

## Purpose

`aoa-stats` now ships a narrow repo-local MCP server so Codex can inspect the
derived observability layer without turning it into workflow authority, proof
authority, or quest-state authority.

This surface is intentionally:

- read-only
- active-summary-surface-first
- boundary-aware
- repo-local
- non-sovereign

## Start posture

When using this MCP:

1. call `stats_boundary_rules` first when there is any risk of overclaiming
2. call `stats_catalog` before reading a specific surface
3. read the catalog entry's strength metadata before trusting a summary
4. prefer `stats_surface_read(..., mode="preview")`
5. expand to `mode="full"` only when the task truly needs the whole payload

If semantics matter, go back to the owner repo. `aoa-stats` stays derived.

## Tools

- `stats_catalog`: read the active summary catalog, preferring `state/generated/summary_surface_catalog.min.json` when a refreshed live state is present and otherwise falling back to `generated/summary_surface_catalog.min.json`
- `stats_surface_read`: read one active summary surface by `surface_name`, or one exact surface by `surface_ref`; the payload wrapper includes the matched `surface_profile` when the catalog can resolve it
- `stats_source_registry`: inspect `config/live_receipt_sources.json`
- `stats_boundary_rules`: reground on `docs/BOUNDARIES.md` and `docs/ARCHITECTURE.md`

## Resources

- `aoa-stats://catalog`
- `aoa-stats://source-registry`
- `aoa-stats://boundaries`
- `aoa-stats://surface/{name}`

## Local run

Install the optional MCP dependency:

```bash
python -m pip install -r requirements-mcp.txt
```

Run the focused MCP tests:

```bash
python -m pytest -q tests/test_aoa_stats_mcp_state.py
```

Start the STDIO server from the repo root:

```bash
python scripts/aoa_stats_mcp_server.py
```

## Project-level Codex wiring

The AoA workspace-level Codex config can wire this repo-local server with:

```toml
[mcp_servers.aoa_stats]
command = "python3"
args = ["scripts/aoa_stats_mcp_server.py"]
cwd = "/srv/aoa-stats"
```

Keep the wiring project-scoped. Do not mirror personal sandbox or model
defaults into the project layer.
