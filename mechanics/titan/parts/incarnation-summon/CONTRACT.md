# Contract

- Incarnation reads only the exact committed roster/session examples named by
  its authored profile. The projection must reject duplicate identities,
  missing Titans, active/locked disagreement, or gate disagreement across the
  three inputs.
- Incarnation counts are derived only after cross-owner coherence succeeds.
  They remain weaker than current identity, gate, summon, or runtime state.
- Summon v1 consumed no owner ledger, so its four-zero baseline is retired. No
  builder, generated payload, public catalog entry, or live materialization may
  remain; the schema is retained only as contract history and the retired
  profile only as a cleanup/provenance tombstone.
- Roster state cannot be converted into invoked-agent, report, finding, or
  memory-candidate counts. SDK helper defaults cannot be converted into owner
  observations.
- Incarnation remains reference-only. A future observed Summon projection
  requires a new active profile, current owner producer, and refresh route that
  observes the selected owner input; the tombstone cannot be reactivated.
- aoa-stats may derive and publish bounded observations only. The result never
  becomes proof, routing, gate, identity, summon, or workflow truth.
- Every part-local or retained public payload route is declared in
  `mechanics/topology.json` and linked from `stats/read-models/`.
