# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/antifragility/parts/via-negativa/tests/test_via_negativa_checklist.py
```

See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

These checks prove the authored question, reciprocal route, checklist order,
owner/provenance stop lines, and checklist-only source posture. The checklist
is human review guidance: its presence does not prove a review occurred, and
no automated merge, move, suppress, quarantine, deprecate, or delete action is
claimed.
