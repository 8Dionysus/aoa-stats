# audit mechanic

`mechanics/audit/` is the active aoa-stats implementation of the common
`audit` mechanic.

Makes coverage, detection, drift, skill-use, and object-observation gaps visible while returning judgment to owners.

Start with `PARTS.md`, then use the selected part's `README.md`,
`CONTRACT.md`, and `VALIDATION.md`.

The live-receipt projections use three deliberately bounded implementation
seams:

- `src/aoa_stats_builder/core_skill_observation.py` derives both the bounded
  core-skill application view and the advisory surface-detection view from the
  same finish-stage receipt family. Its cross-part contract is exercised by
  `mechanics/audit/tests/test_core_skill_observation.py`.
- `src/aoa_stats_builder/object_observation.py` derives occurrence and recency
  observations across the active receipt set. Its operation-specific contract
  is exercised by
  `mechanics/audit/parts/object-observation/tests/test_object_observation.py`.
- `src/aoa_stats_builder/source_coverage.py` audits the admitted feed against
  an optional registry baseline. Ordering, conservation, non-mutation,
  dominance, and missing-registry behavior are exercised by
  `mechanics/audit/parts/source-coverage/tests/test_source_coverage.py`.

The published profiles, schemas, and generated read models keep their stable
root routes. `scripts/build_views.py` keeps compatibility aliases and repo-wide
fan-out, not another implementation or proof home for these cores.

Cycle 10 is an extraction-only boundary. It deliberately preserves historical
ordered-input behavior: Surface Detection keeps its legacy context and count
coercion buckets, while Object Observation distinguishes input-first,
temporal-latest, and input-last-within-family fields. See the part contracts
for the exact semantics and their authority stop-lines.
