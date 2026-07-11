# Epistemic observability validation

Run from the repository root:

```bash
python mechanics/agon/parts/epistemic-observability/scripts/build_agon_epistemic_stats_observability_registry.py --check
python mechanics/agon/parts/epistemic-observability/scripts/validate_agon_epistemic_stats_observability.py
python -m pytest -q mechanics/agon/parts/epistemic-observability/tests/test_agon_epistemic_stats_observability.py
```

The validator checks source metadata, item and registry schemas, uniqueness,
forbidden effects, and generated drift.
