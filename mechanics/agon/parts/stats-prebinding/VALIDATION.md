# Stats prebinding validation

Run from the repository root:

```bash
python mechanics/agon/parts/stats-prebinding/scripts/build_agon_stats_prebinding_registry.py --check
python mechanics/agon/parts/stats-prebinding/scripts/validate_agon_stats_prebindings.py
python -m pytest -q mechanics/agon/parts/stats-prebinding/tests/test_agon_stats_prebindings.py
```

The checks prove deterministic publication, the declared record key, unique
references, and the pre-protocol stop lines.
