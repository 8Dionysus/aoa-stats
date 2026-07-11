# Contract

- Incarnation reads only the exact committed roster/session examples named by
  its authored profile. The projection must reject duplicate identities,
  missing Titans, active/locked disagreement, or gate disagreement across the
  three inputs.
- Incarnation counts are derived only after cross-owner coherence succeeds.
  They remain weaker than current identity, gate, summon, or runtime state.
- Summon v1 consumes no owner ledger. Its four zeros are an explicit
  `no-observed-ledger` compatibility baseline and must not be interpreted as
  observed zero activity.
- Roster state cannot be converted into invoked-agent, report, finding, or
  memory-candidate counts. SDK helper defaults cannot be converted into owner
  observations.
- Both surfaces remain reference-only. Live activation requires a current
  owner producer plus a refresh route that observes the selected owner input.
- aoa-stats may derive and publish bounded observations only. The result never
  becomes proof, routing, gate, identity, summon, or workflow truth.
- Every part-local or retained public payload route is declared in
  `mechanics/topology.json` and linked from `stats/read-models/`.
