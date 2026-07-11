# Consumer regrounding contract

## Purpose

Expose enough information about a derived stats surface and its current intake
coverage for a consumer to find stronger owner truth and avoid overreading the
projection.

## Inputs

- surface definitions from the `surface_catalog` stats family
- owner-truth input references and authority ceilings
- the active live source registry when available
- derived receipt coverage and skew observations

## Outputs

- surface profiles with input posture, owner-truth inputs, authority ceiling,
  consumer risk, and live-state capability
- source-coverage summaries with missing, unexpected, or dominant-source flags

## Invariants

- every catalog profile identifies stronger owner inputs
- an authority ceiling stays weaker than the named owner truth
- missing registry context remains visible rather than inventing coverage
- coverage skew is a descriptive signal, not an owner-health verdict
- no output approves a route, passes proof, activates workflow, or authorizes a
  mutation
- producer aggregation rules remain owned and tested by the Source Coverage
  Audit part; this consumer part tests catalog exposure and return-to-owner
  interpretation only

## Crosswalk

This part operates on stats source-family id `surface_catalog`. The reciprocal
route is recorded in `stats/source_home.manifest.json` and
`mechanics/topology.json`.

## Current payload route

Focused consumer-regrounding tests are part-local. The stable public catalog
schema/output and compatibility validator remain at the root routes enumerated
in the topology.
