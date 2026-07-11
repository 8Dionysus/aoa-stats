# Validation

```bash
python -m pytest -q mechanics/experience/parts/governance-runtime-signals/tests/test_experience_wave4_seed_contracts.py
```

The test validates all five local pairs and rejects widened types, enums,
constants, unknown fields, and invalid numeric ranges.
