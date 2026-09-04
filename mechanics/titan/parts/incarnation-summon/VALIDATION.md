# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/titan/parts/incarnation-summon/tests tests/test_build_views.py tests/test_stats_source_home.py tests/test_mechanics_topology.py tests/test_summary_surface_catalog.py
```

See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

The part-local suite proves facade delegation, exact cross-owner coherence,
bounded permutation invariance, rejection of identity/state/gate drift,
conservation, non-mutation, schema validity, committed Incarnation output
parity, and the absence of a Summon builder, active profile, generated output,
or catalog entry while its cleanup tombstone remains valid.
