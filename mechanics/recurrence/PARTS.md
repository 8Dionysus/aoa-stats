# Recurrence parts

## Active parts

| Part | Purpose | Stats source-family id | Payload posture |
| --- | --- | --- | --- |
| `live-receipt-refresh` | audit registered publishers and rebuild bounded live views | `intake_contract` | part-local registry, templates, guide, and tests; root public commands |
| `component-manifests` | keep stats component and hook recurrence declarations discoverable | `surface_catalog` | part-local declarations, projection contract, examples, and boundaries |
| `component-refresh` | describe recurring component-refresh posture without becoming refresh truth | `read_models` | part-local docs, examples, and focused test; root public schema and output |
| `continuity-window` | expose a bounded continuity-window read model without continuity authority | `read_models` | part-local docs and example; root public schema and output |
| `repeated-window` | derive repeated-window counts without treating repetition as proof | `read_models` | route contract only; root public schema, output, and shared builder |

`mechanics/topology.json` records the exact payload and compatibility routes.
Every part must keep its reciprocal source-family route in
`stats/source_home.manifest.json`.
