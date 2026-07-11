# summary-catalog-artifact-bundle

Defines the public summary-catalog bundle and owns its operation-specific
validator under `scripts/validate_abyss_machine_summary_catalog_bundle.py`.

The root script with the same name is a compatibility entrypoint. Public
manifest, schemas, generated outputs, bundle, registry, and subject-store
paths stay at their declared publication paths because consumers depend on
those paths.
