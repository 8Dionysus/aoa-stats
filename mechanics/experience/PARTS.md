# Experience parts

| Part | Owned payload | Focused validation |
| --- | --- | --- |
| `micro-friction-receipts` | 1 doc, 3 examples, 3 schemas, 1 test | `python -m pytest -q mechanics/experience/parts/micro-friction-receipts/tests/test_micro_friction_contracts.py` |
| `adoption-federation-harvest` | 11 docs, 14 examples, 14 schemas, 1 test | `python -m pytest -q mechanics/experience/parts/adoption-federation-harvest/tests/test_experience_wave3_seed_contracts.py` |
| `governance-runtime-signals` | 9 docs, 5 examples, 5 schemas, 1 test | `python -m pytest -q mechanics/experience/parts/governance-runtime-signals/tests/test_experience_wave4_seed_contracts.py` |
| `release-watch-office-health` | 15 docs, 17 examples, 16 schemas, 2 tests | `python -m pytest -q mechanics/experience/parts/release-watch-office-health/tests` |

`release_health_summary_v1.json` belongs only to
`release-watch-office-health`; both historical example shapes are validated
there so the schema does not acquire two active owners.
