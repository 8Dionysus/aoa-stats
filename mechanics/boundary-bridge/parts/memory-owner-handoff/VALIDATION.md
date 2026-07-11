# Validation

Run the focused core/adapter contract first, then the committed projection and
live-admission checks:

```bash
python -m pytest -q mechanics/boundary-bridge/parts/memory-owner-handoff/tests/test_memory_movement_summary.py
python scripts/build_views.py --check
python -m pytest -q mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py tests/test_summary_surface_catalog.py
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
```

The focused suite proves the exact four roots, deterministic discovery,
catalog/object exactness, timestamp refusal, deep bundle immutability,
filesystem-free non-mutating projection, schema validity, and byte parity with
`generated/memory_movement_summary.min.json`.

The live-refresh suite proves the separate operational claim: reference-only
Memory Movement is not built or advertised in local live state and stale
managed copies are removed.
