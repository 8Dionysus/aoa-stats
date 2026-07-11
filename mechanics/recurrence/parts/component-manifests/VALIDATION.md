# Component manifests validation

## Current checks

Run from the repository root:

```bash
python mechanics/recurrence/parts/component-manifests/scripts/validate_component_manifests.py
python -m pytest -q mechanics/recurrence/parts/component-manifests/tests/test_component_manifests.py
python scripts/validate_mechanics_topology.py
python scripts/validate_stats_source_home.py
```

The records remain descriptive only; a green component/hook contract is not
proof that a publisher, watcher, or runtime hook is active.
