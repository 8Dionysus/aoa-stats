# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python -m pytest -q mechanics/titan/parts/incarnation-summon/tests tests/test_build_views.py tests/test_stats_source_home.py tests/test_mechanics_topology.py tests/test_summary_surface_catalog.py
```

The part-local suite proves facade delegation, exact cross-owner coherence,
bounded permutation invariance, rejection of identity/state/gate drift,
conservation, non-mutation, schema validity, explicit no-ledger semantics, and
committed output parity.
