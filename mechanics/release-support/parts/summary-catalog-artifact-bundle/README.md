# summary-catalog-artifact-bundle

Defines the public summary-catalog bundle and owns its operation-specific
validator under `scripts/validate_abyss_machine_summary_catalog_bundle.py`.

The root script with the same name is a compatibility entrypoint. Public
manifest, schemas, and generated outputs stay at their retained paths. Bundle,
registry, and subject-store paths are declared on-demand materialization routes
under ignored `dist/`; a clean checkout is not required to contain them.
