# Recurrence parts

## Active parts

| Part | Purpose | Stats source-family id | Payload posture |
| --- | --- | --- | --- |
| `live-receipt-refresh` | audit registered publishers and materialize profile-admitted live views | `intake_contract` | part-local registry, templates, guide, and tests; root public commands |
| `component-manifests` | keep stats component and hook recurrence declarations discoverable | `surface_catalog` | part-local declarations, projection contract, examples, and boundaries |
| `component-refresh` | preserve one committed Component Refresh reference projection without becoming current refresh truth | `read_models` | part-local docs, examples, and focused tests; importable core/reference adapter; root public schema and committed output |
| `continuity-window` | preserve one committed cross-owner Continuity Window reference projection without claiming current continuity or reanchor success | `read_models` | part-local docs, example, and focused tests; importable validation/projection core and reference adapter; root public schema and committed output |
| `repeated-window` | derive observed calendar-date receipt counts without treating a bucket as proof of change or recurrence | `read_models` | part-local invariant tests; importable pure core; root public schema, output, and compatibility facade |

`mechanics/topology.json` records the exact payload and compatibility routes.
Every part must keep its reciprocal source-family route in
`stats/source_home.manifest.json`.
