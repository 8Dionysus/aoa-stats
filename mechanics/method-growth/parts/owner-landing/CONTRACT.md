# Contract

- Admit only structurally complete reviewed landing bundles and seed landing
  traces with parseable observation times and evidence references.
- Preserve the earliest reviewed time for duration calculation while the
  latest reviewed bundle supplies the current descriptive owner and posture.
- Count an outcome only when it is explicit in a seed landing trace; unknown
  outcomes may be counted but never invented as a standard duration bucket.
- Publish only the fields admitted by
  `schemas/owner-landing-summary.schema.json` at the stable route
  `generated/owner_landing_summary.min.json`.
- The result remains weaker than owner-local status surfaces and never becomes
  owner acceptance, routing, proof, gate, identity, or workflow truth.
