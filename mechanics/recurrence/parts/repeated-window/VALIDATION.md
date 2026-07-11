# Repeated window validation

Run from the repository root:

```bash
python -m json.tool schemas/repeated-window-summary.schema.json >/dev/null
python -m json.tool generated/repeated_window_summary.min.json >/dev/null
python -m pytest -q mechanics/recurrence/parts/repeated-window/tests/test_repeated_window.py
python scripts/build_views.py --check
```

These checks cover permutation invariance, count conservation, object identity,
input non-mutation, root-facade hook delegation, public schema validity, and
committed output bytes. This part intentionally has no duplicated schema or
generated output.
