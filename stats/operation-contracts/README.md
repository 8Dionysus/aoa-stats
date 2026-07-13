# Operation contracts source family

This source family authors active mechanic-linked stats contracts whose result
is not a public `summary_surface_catalog` read model. One record at
`active/<operation_id>.operation.json` answers what aoa-stats may observe,
which evidence is truly bound, where authority stops, and where interpretation
or action returns.

Active inventory is the set of records under `active/` checked against
`stats/source_home.manifest.json` and `mechanics/topology.json`. Payload stays
part-local; records do not copy metric lists, schemas, examples, scripts,
tests, or generated registries. The family must remain non-empty, but its
current cardinality is derived from that reciprocal crosswalk rather than
treated as a stable contract.

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
source/evidence pair. Read the record and validator registry for current
binding state rather than relying on a family-level status sentence.

`operation-contract.schema.json` constrains the records. The family inventory
is [`stats/source_home.manifest.json`](../source_home.manifest.json), and the
reciprocal part links are in
[`mechanics/topology.json`](../../mechanics/topology.json).
