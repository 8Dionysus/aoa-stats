# aoa-stats Artifact Bundles

This directory holds repo-local OS Abyss artifact bundle manifests for derived
stats readmodels.

The manifests do not make stats stronger than owner-local receipts, verdicts,
or source surfaces. They only describe how public generated observability
readmodels are verified for ABI and SBOM-lite subject inventory.

Current bundle:

- `summary_surface_catalog.bundle.json` verifies
  `generated/summary_surface_catalog.min.json` as a
  `derived_observability_readmodel_catalog`.

```bash
python scripts/validate_abyss_machine_summary_catalog_bundle.py
```

The validator also rehearses registry latest selection, consumer trust-gate
admission, isolated subject-store materialization, corrupted ABI/SBOM rejection,
unverified latest rejection, private marker rejection, and terminal revocation.
