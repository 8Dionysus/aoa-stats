# Validation

Run from the repository root:

```bash
python -m pytest -q mechanics/rpg/parts/route-progression/tests/test_route_progression.py
```

See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

The focused part-local test constrains the seven-axis whitelist, falsey route
fallback, Python integer compatibility including booleans, list-length caution
counting, `(observed_at, event_id)` latest selection, missing-versus-null
verdict normalization, explicit rejection of semantic-only owner receipts,
non-mutation, root compatibility aliases, schema validity, and committed-output
parity. Refresh tests prove the reference-only output is omitted and stale
copies are cleaned. Catalog tests prove consumer re-grounding leads with the
exact tracked `aoa-skills` semantic schema and example rather than the legacy
numeric compatibility fixture. These checks do not prove rank, mastery,
unlock, navigation, or owner progression truth.
