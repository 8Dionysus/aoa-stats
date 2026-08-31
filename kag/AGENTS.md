# AGENTS.md

## Applies to

This card applies to the local KAG provider home and its source-linked records.

## Role

`kag/` exposes source-linked stats navigation and supporting projections. The
authored stats source home remains primary; generated catalogs and KAG views
are weaker access surfaces and never replace authored meaning.

## Conditional route

For a KAG question, follow the selected source record and its owner route.
Open a local README when human orientation is material, then inspect only the
provider record, schema, edge, or projection named by the question. The
machine-readable stats crosswalk is `stats/source_home.manifest.json`.

## Boundaries

- Provider records retain exact source refs and owner handles.
- KAG composition may aid lookup but cannot grant stats, proof, runtime, or
  owner authority.
- Do not copy owner manifests, evidence, runtime state, raw sessions, or
  one-session worktree status here.
- Missing, stale, or unregistered source evidence remains visible.

## Conditional validation and closeout

Use the root `VALIDATION.md`, the source-home route, and the named Agon or
provider owner checks when this district changes. Report provider records,
source-return routes, owner validation, `aoa-kag` validation, and the next MCP
consumer route; a projection check is not publication or acceptance evidence.
