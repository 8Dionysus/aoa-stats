# AGENTS.md

## audit mechanic guidance

This package implements the stats-side projection of the common
`Agents-of-Abyss/mechanics/audit` mechanic.

Keep operation-specific docs, examples, supporting contracts, and focused
tests under the nearest part. Published catalog schemas and generated read
models may remain at repository root only when their stable public paths are
declared in `mechanics/topology.json`.

Audit has two deterministic core boundaries:

- `src/aoa_stats_builder/core_skill_observation.py` is shared only by
  `core-skill-application` and `surface-strength-detection`; its focused
  cross-part tests belong in
  `mechanics/audit/tests/test_core_skill_observation.py`.
- `src/aoa_stats_builder/object_observation.py` serves only
  `object-observation`; its focused tests belong under
  `mechanics/audit/parts/object-observation/tests/`.

Do not merge source-coverage or drift-review logic into either core. They have
different source and adapter boundaries. `scripts/build_views.py` is the
repo-wide build facade and retains compatibility aliases only; new projection
logic belongs in the appropriate filesystem-free core.

Registered live receipts remain source-owned evidence. Audit code may consume
the active, supersession-resolved receipt set and publish bounded observations,
but it must not redefine receipt admission, owner success, source health, or
surface authority.

This extraction preserves two ordered-input compatibility contracts:

- Surface Detection places missing, non-mapping, or empty detection context in
  the legacy `activated` bucket, preserves `int(value or 0)` candidate-count
  coercion for upstream-valid payloads, and reports the first and last admitted
  receipt in supplied order within each date window. The bucket name is not
  owner activation truth.
- Object Observation reports the input-first receipt as `first_observed_at`,
  chooses the overall temporal latest receipt by `(observed_at, event_id)`, and
  keeps the input-last evaluation and progression verdict within each event
  family.

These rules are compatibility debt, not new authority. Do not silently
normalize them during extraction; a future semantic correction requires a
separate behavior change and public-output review.

Stats outputs are descriptive and weaker than their named owner sources.
Do not add routing, proof, gate, or workflow authority here.
