# Operation contracts source family

This source family authors active mechanic-linked stats contracts whose result
is not a public `summary_surface_catalog` read model. One record at
`active/<operation_id>.operation.json` answers what aoa-stats may observe,
which evidence is truly bound, where authority stops, and where interpretation
or action returns.

It currently covers bounded Agon registries, Experience observation
contracts, the via-negativa review checklist, and Titan memory/runtime
projection specifications. Their active payload stays part-local. These
records do not copy metric lists, schemas, examples, scripts, tests, or
generated registries.

The four honest input postures are:

- `seed_registry_compiler` for deterministic Agon candidate registries;
- `schema_example_contracts` for Experience contract portfolios whose examples
  are not current measurements;
- `documentation_checklist` for via-negativa review guidance;
- `documentation_projection_spec` for Titan projections without a local
  builder.

Each owner input separately states its evidence binding: `symbolic_unbound`
when no route is named, `declared_reference_only` when a route is named but not
read, and `bound_current_source` only when the operation actually consumes the
named current source. A bound claim also needs a mechanic-local
`binding_evidence_ref` and an explicit validator registration of the exact
source/evidence pair. No current operation has that registration.

`operation-contract.schema.json` constrains the records. The family inventory
is [`stats/source_home.manifest.json`](../source_home.manifest.json), and the
reciprocal part links are in
[`mechanics/topology.json`](../../mechanics/topology.json).
