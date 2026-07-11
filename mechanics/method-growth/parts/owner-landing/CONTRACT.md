# Contract

- The committed build currently reads the Owner Landing examples in
  `stats/intake-contract/examples/session_harvest_family.receipts.example.json`;
  those examples demonstrate the receipt and projection contract but do not
  report current owner activity.
- Admit only structurally complete reviewed landing bundles and seed landing
  traces with parseable observation times and evidence references.
- Preserve the earliest reviewed time for duration calculation while the
  latest reviewed bundle supplies the current descriptive owner and posture.
- Count an outcome only when it is explicit in a seed landing trace; unknown
  outcomes may be counted but never invented as a standard duration bucket.
- Publish only the fields admitted by
  `schemas/owner-landing-summary.schema.json` at the stable route
  `generated/owner_landing_summary.min.json`.
- Keep deterministic receipt-to-summary rules in the filesystem-free shared
  Method Growth core at `src/aoa_stats_builder/candidate_lifecycle.py`; input
  choice, build orchestration, and publication do not move owner truth into
  that core.
- The result remains weaker than owner-local status surfaces and never becomes
  owner acceptance, routing, proof, gate, identity, or workflow truth.

## Live boundary

- No real owner-local publisher or current receipt has been found for
  `reviewed_owner_landing_receipt` or `seed_owner_landing_trace_receipt`.
- The active profile therefore keeps `live_state_capable: false`; accepted
  event-kind vocabulary and a buildable pure core are not live evidence.
- Live refresh must not invoke the Owner Landing reference builder, materialize
  the output, or advertise it in the live catalog, and stale managed runtime
  copies must be removed on both non-empty and empty refresh paths.
- Future activation requires a named owner publisher, current receipts backed
  by owner-local status surfaces, and a tested refresh observation route for
  the publisher's receipt log.
