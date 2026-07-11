# AGENTS.md

## Recurrence agent guide

This package owns the `aoa-stats` participation in the common Recurrence
mechanic. Read `../AGENTS.md`, this package's `README.md`, `PARTS.md`, and
`PROVENANCE.md` before editing a part.

## Active parts

- `parts/live-receipt-refresh/`
- `parts/component-manifests/`
- `parts/component-refresh/`
- `parts/continuity-window/`
- `parts/repeated-window/`

## Boundary

- `live-receipt-refresh` operates on the `intake_contract` source family.
- `component-manifests` operates on the `surface_catalog` source family.
- `component-refresh`, `continuity-window`, and `repeated-window` operate on
  the `read_models` source family.
- Source repositories retain ownership of the receipts and facts being
  observed.
- This package may describe deterministic refresh, recurrence declarations,
  and bounded recurring windows; it must not claim proof, routing, owner
  health, continuity legitimacy, or source-state authority.

## Edit law

- Keep operation-owned docs, examples, registries, templates, declarations,
  and focused tests inside their active part.
- Keep root `scripts/` commands when they are public compatibility entrypoints;
  they must resolve their canonical part-local payload explicitly.
- Keep published read-model schemas and generated summaries at their root
  public routes when a part declares that compatibility exception.
- Update `PARTS.md`, `PROVENANCE.md`, the machine-readable topology, and the
  matching stats source-family crosswalk together when a route changes.
- Do not duplicate a payload between a root district and a part.
- Run the focused commands named by the touched part's `VALIDATION.md`.
