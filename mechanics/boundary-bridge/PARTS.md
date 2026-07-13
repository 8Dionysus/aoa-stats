# Boundary bridge parts

## Active parts

| Part | Purpose | Stats source-family id | Payload route status |
| --- | --- | --- | --- |
| `receipt-abi-crossing` | admit source-owned event families through the shared stats envelope | `intake_contract` | mixed localized/public |
| `consumer-regrounding` | expose catalog and coverage signals that point back to stronger owners | `surface_catalog` | mixed localized/public |
| `memory-owner-handoff` | summarize reviewed memory movement and return consumers to aoa-memo | `read_models` | mixed localized/public |
| `measurement-packet-crossing` | validate and combine compatible owner-local packets without taking metric ownership | `measurement_contract`, `federation` | localized |

The placement inventory in `mechanics/topology.json` distinguishes localized
payload from retained public contracts, generated outputs, and compatibility
entrypoints.
