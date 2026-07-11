# AGENTS.md

## Boundary bridge parts agent guide

Each directory below this one is an active, bounded crossing contract.

Before editing a part:

1. read `../AGENTS.md` and `../PARTS.md`
2. read the part's `README.md`, `CONTRACT.md`, and `VALIDATION.md`
3. verify its `stats_source_family_ref` and current payload routes in
   `mechanics/topology.json`
4. identify the stronger owner on both sides of the crossing

Do not add a part without an evidenced crossing, an explicit source-family
crosswalk, bounded inputs and outputs, authority stop-lines, and a truthful
validation route.
