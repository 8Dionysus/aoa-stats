# Continuity window validation

Run from the repository root:

```bash
python -c 'import json, pathlib; from jsonschema import Draft202012Validator; root=pathlib.Path("mechanics/recurrence/parts/continuity-window"); schema=json.loads(pathlib.Path("schemas/continuity-window-summary.schema.json").read_text()); example=json.loads((root/"examples/continuity_window_summary.example.json").read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(example)'
python -m pytest -q tests/test_build_views.py -k continuity_window_summary
python scripts/build_views.py --check
```

These checks prove the part-local example still conforms to the root public
contract and that the shared builder preserves the derived-only stop lines.
