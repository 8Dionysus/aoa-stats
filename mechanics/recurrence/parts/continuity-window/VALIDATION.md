# Continuity window validation

Run from the repository root:

```bash
python -c 'import json, pathlib; from jsonschema import Draft202012Validator; root=pathlib.Path("mechanics/recurrence/parts/continuity-window"); schema=json.loads(pathlib.Path("schemas/continuity-window-summary.schema.json").read_text()); example=json.loads((root/"examples/continuity_window_summary.example.json").read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(example)'
python -m pytest -q mechanics/recurrence/parts/continuity-window/tests
```

See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

These checks prove the part-local example conforms to the public contract, the
reference adapter and filesystem-free projection preserve owner-chain
coherence, status cannot manufacture reanchor success, the root facade remains
compatible, and live admission follows the authored profile.
