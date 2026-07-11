# Contract

- Admit candidate lineage only from `harvest_packet_receipt` payloads whose
  evidence density is explicitly `reviewed`.
- Preserve explicitly recorded stages; do not infer seeded, planted, proved,
  promoted, merged, superseded, or dropped state from a nearby stage.
- Choose the latest explicit record per candidate by recorded lifecycle time
  while keeping source timestamps and owner hypotheses descriptive.
- Publish only the fields admitted by
  `schemas/candidate_lineage_summary.schema.json` at the stable route
  `generated/candidate_lineage_summary.min.json`.
- The result remains weaker than reviewed owner-local lineage and never
  becomes promotion, routing, proof, gate, identity, or workflow truth.
