# Runtime Closeout validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/checkpoint/parts/runtime-closeout/tests/test_runtime_closeout.py
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q tests/test_build_views.py tests/test_stats_source_home.py tests/test_mechanics_topology.py
```

Focused proof constrains exact event-kind admission, identity fallback,
deterministic grouping and latest selection, count/default behavior, truth
projection, non-mutation, schema validity, root compatibility aliases, and
committed-output byte parity. Live-refresh tests separately prove that the
reference-only builder is not invoked and stale runtime copies are removed.

These checks do not prove that the historical wave receipt is the current
owner ABI. Re-activation proof must include a real receipt from the chosen
current producer plus registry and watcher parity.
