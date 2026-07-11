# Component manifests contract

## Purpose

Keep stats component recurrence declarations and hook records discoverable as
bounded descriptors of recurring stats surfaces.

## Inputs

- component declarations under `manifests/components/`
- hook declarations under `manifests/hooks/`
- the recurrence stats projection schema and example
- source-family identity from `surface_catalog`

## Outputs

- declarative component identity, owner references, surface references, and
  recurrence posture
- declarative hook records associated with those components

## Invariants

- a component declaration does not prove that its publisher, refresh, or hook
  is currently running
- a hook record does not become runtime or scheduling authority
- a declaration preserves stronger owner and evidence references
- stats recurrence records stay descriptive and derived-only
- every component manifest has exactly one same-named hook manifest
- component and hook identities agree after legacy separator variants are
  normalized
- path-like refs and executable commands resolve to current active routes; no
  former flat Agon path may return

## Crosswalk

This part operates on stats source-family id `surface_catalog`. The reciprocal
route is recorded in `stats/source_home.manifest.json` and
`mechanics/topology.json`.

## Payload route

Declarations, projection contract, example, and boundary docs are canonical
inside this part. Their referenced public stats surfaces and stronger-owner
artifacts remain at the routes named by each record.
