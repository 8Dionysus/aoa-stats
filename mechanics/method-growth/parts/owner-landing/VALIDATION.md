# Validation

Run the cross-routed source and placement checks from the repository root:

```bash
python -m pytest -q mechanics/method-growth/tests/test_candidate_lifecycle.py
python -m pytest -q mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py
python scripts/build_views.py --check
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
```

The package-level test is intentional: it constrains the shared lifecycle core
and the root compatibility facade across all three Method Growth parts. Its
synthetic receipts prove deterministic projection behavior, not the existence
of a current owner publisher.

The live-refresh test must independently prove that Owner Landing is outside
the authored live allowlist, that its builder is not called by a live run, and
that an older `state/generated/owner_landing_summary.min.json` is removed on
both non-empty and empty refresh paths. A future activation change must add
focused evidence for the real owner publisher, current receipts, and their
refresh observation route before changing the profile selector.
