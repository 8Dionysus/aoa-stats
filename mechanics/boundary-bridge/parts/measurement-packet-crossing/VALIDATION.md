# Measurement packet crossing validation

Focused semantic proof lives in this part's `tests/` district. Schema,
inventory, and optional local-port validation are owned by
`scripts/validate_stats_protocol.py`. The repository-wide executable route is
`scripts/release_check.py`.

The proof covers the invariants named in `CONTRACT.md`, including negative
cases that reject false aggregation and false live or privacy posture.

Run:

```bash
python -m pytest -q mechanics/boundary-bridge/parts/measurement-packet-crossing/tests
python scripts/validate_stats_protocol.py
```

The examples file is a positive/negative corpus container, not one receipt.
Focused tests validate each admitted example and each named mutation
separately. Producers validate one concrete receipt path with
`python scripts/validate_stats_protocol.py --outcome-receipt <path>`.

The C10 corpus also proves normalized self-digest drift detection, balanced
holdout and always-shadow bindings, task/consumer and host refs, independent
evaluator evidence, explicit operator intervention posture, access-count
exclusion, semantic-transition denial, and policy freeze when the eval plane
is degraded or unavailable.

`test_outcome_qualified_utility.py` additionally proves that aggregation
rejects invalid C10, does not reward terminal success without action change,
keeps pending delayed evidence partial, excludes access count, rejects
unknown or owner-rejected utility evidence and duplicate delivery, and emits
no proof, semantic, or effect authority.

`test_agent_local_federation_aggregate.py` proves that Phase 12 promotion
results and operator minutes reconcile, while promotion and proof authority
remain forbidden.
