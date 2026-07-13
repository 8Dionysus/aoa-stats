# AGENTS.md

## Boundary bridge agent guide

This package owns the `aoa-stats` participation in the common Boundary Bridge
mechanic. Read `../AGENTS.md`, this package's `README.md`, `PARTS.md`, and
`PROVENANCE.md` before editing a part.

## Active parts

- `parts/receipt-abi-crossing/`
- `parts/consumer-regrounding/`
- `parts/memory-owner-handoff/`

## Boundary

- `receipt-abi-crossing` operates on the `intake_contract` source family.
- `consumer-regrounding` operates on the `surface_catalog` source family.
- `memory-owner-handoff` operates on the `read_models` source family.
- `measurement-packet-crossing` operates on the `measurement_contract` and
  `federation` source families.
- Payload owners retain the meaning of the facts inside a receipt.
- Consumers retain their own policy, route, proof, and mutation decisions.
- This package owns the stats crossing contract, not either side's stronger
  authority.

## Edit law

- Keep focused operation payload part-local. Retain only the public contracts,
  generated outputs, and compatibility commands explicitly listed in
  `../topology.json`.
- Update `PARTS.md`, `PROVENANCE.md`, and the topology together when a part
  route changes.
- Update the matching stats source-family crosswalk in both directions.
- Do not widen receipt admission without a payload owner and a bounded stats
  consumer.
- Do not turn a consumer warning or regrounding hint into an action verdict.
- Do not aggregate a measurement packet across an undeclared compatibility
  axis or turn a local definition into central domain meaning.
- Follow the focused executable routes named by the touched part's
  `VALIDATION.md`.
