# Component refresh validation

Run from the repository root:

```bash
python -m pytest -q mechanics/recurrence/parts/component-refresh/tests/test_component_refresh_summary.py
python -m pytest -q tests/test_build_views.py -k component_refresh_summary
python scripts/build_views.py --check
```

The focused part test proves route discoverability, schema/example validity,
and canonical owner-law refs. Builder checks prove deterministic publication
at the root public output route.
