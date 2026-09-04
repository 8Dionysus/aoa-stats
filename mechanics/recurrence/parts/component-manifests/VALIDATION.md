# Component manifests validation

## Current checks

Run from the repository root:

```bash
python mechanics/recurrence/parts/component-manifests/scripts/validate_component_manifests.py
python -m pytest -q mechanics/recurrence/parts/component-manifests/tests/test_component_manifests.py
```

See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

The records remain descriptive only; a green component/hook contract is not
proof that a publisher, watcher, or runtime hook is active.
