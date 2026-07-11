# audit provenance

The common mechanic vocabulary comes from
`Agents-of-Abyss/mechanics/audit`.

The payload in this package was regrouped from aoa-stats root districts by
operation, preserving stable public publication paths. Deterministic root
builder logic for core-skill application and surface detection moved to the
shared `src/aoa_stats_builder/core_skill_observation.py` core. Object grouping
and recency logic moved independently to
`src/aoa_stats_builder/object_observation.py`.

The root `scripts/build_views.py` names remain compatibility aliases and
repo-wide orchestration routes. The focused proof routes are
`mechanics/audit/tests/test_core_skill_observation.py` for the shared pair and
`mechanics/audit/parts/object-observation/tests/test_object_observation.py` for
the separate object boundary.

Live observations come from registered owner receipt streams after shared
admission and supersession resolution. Those streams retain event, object,
application, and detection-context authority. aoa-stats only derives read
models; a legacy `activated` compatibility bucket created from missing or empty
context does not manufacture owner activation truth, and ordered-input object
fields do not replace owner chronology. Neither projection may declare owner
success or turn an observation into routing, gate, or proof truth.

The extraction intentionally preserved the root builder's existing bytes and
ordered-input behavior. Surface candidate counts retain legacy integer
coercion and therefore depend on upstream-valid payloads. Object first/latest
and family-verdict fields retain their distinct input-order and temporal rules.
These are recorded compatibility debts rather than newly accepted domain law.

The topology records current localized and retained public routes only;
former root placement remains recoverable from Git rename history.
