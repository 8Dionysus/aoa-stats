# Validation

```bash
python -m pytest -q \
  mechanics/experience/parts/release-watch-office-health/tests/test_experience_wave2_seed_contracts.py \
  mechanics/experience/parts/release-watch-office-health/tests/test_experience_wave5_seed_contracts.py
```

Both tests must pass together because the two portfolios share one release
health schema.
