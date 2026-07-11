# object-observation

Publishes occurrence and recency observations for source objects.

This part groups the active, supersession-resolved receipt set by object
identity and publishes bounded occurrence and recency observations. It has a
separate core because its input is wider than the core-skill receipt family.

- source profile: `stats/read-models/active/object_summary.profile.json`
- filesystem-free core: `src/aoa_stats_builder/object_observation.py`
- focused part-local test:
  `mechanics/audit/parts/object-observation/tests/test_object_observation.py`
- public schema: `schemas/object-summary.schema.json`
- generated read model: `generated/object_summary.min.json`
- root compatibility facade: `scripts/build_views.py`

The part-local test route is declared in `mechanics/topology.json`. Stable
public schema and generated routes remain at root for consumers. The extraction
preserves three distinct compatibility selectors: input-first observation,
temporal-latest receipt, and input-last evaluation/progression verdict within
each family. These fields must not be generalized into one chronology rule.
