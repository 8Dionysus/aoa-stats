# Validation

Run the part-local contract test and public compatibility command, then the
cross-topology checks:

```bash
python -m pytest -q mechanics/release-support/parts/summary-catalog-artifact-bundle/tests/test_summary_catalog_artifact_bundle.py
python scripts/validate_abyss_machine_summary_catalog_bundle.py
python scripts/validate_abyss_machine_summary_catalog_bundle.py --ephemeral
python scripts/build_views.py --check
python scripts/validate_mechanics_topology.py
```

The direct command materializes the declared ignored `dist/` publication
paths. Repo-level release checks use `--ephemeral` for the same full trust
roundtrip without changing the checkout.
