# Repeated window validation

Run from the repository root:

```bash
python -m json.tool schemas/repeated-window-summary.schema.json >/dev/null
python -m json.tool generated/repeated_window_summary.min.json >/dev/null
python -m pytest -q tests/test_build_views.py -k expected_surface_counts
python scripts/build_views.py --check
```

These checks cover the stable root public routes and the shared deterministic
builder. This part intentionally has no duplicated schema or generated output.
