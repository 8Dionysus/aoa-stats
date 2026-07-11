# AGENTS.md

## Recurrence parts agent guide

Each directory below this one is an active, bounded recurrence operation.

Before editing a part:

1. read `../AGENTS.md` and `../PARTS.md`
2. read the part's `README.md`, `CONTRACT.md`, and `VALIDATION.md`
3. verify its `stats_source_family_ref` and current payload routes in
   `mechanics/topology.json`
4. preserve owner-source authority and visible freshness limits

When auditing live posture, classify the part's actual source chain before
changing its stats profile. A committed example chain stays reference-only
until a canonical owner-runtime artifact or receipt exists, and missing
occurrence evidence must remain zero or absent rather than inferred from
status.

Do not add a part without an evidenced operation, an explicit source-family
crosswalk, bounded inputs and outputs, and a truthful validation route.

Part-local operation payload is canonical unless the part explicitly names a
root public schema, generated output, or compatibility command. Do not copy a
public exception into the part or move it merely for visual symmetry.
