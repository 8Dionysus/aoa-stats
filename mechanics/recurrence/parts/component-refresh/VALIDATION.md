# Component refresh validation

Run from the repository root:

```bash
python -m pytest -q \
  mechanics/recurrence/parts/component-refresh/tests/test_component_refresh_summary.py \
  mechanics/recurrence/parts/component-refresh/tests/test_component_refresh_projection.py
```

See the nearest owner validation route (../live-receipt-refresh/VALIDATION.md) for this procedure. See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

The focused part test proves route discoverability, schema/example validity,
canonical owner-law refs, filesystem-free projection, and explicit reviewed
example adaptation. Root builder checks prove deterministic committed
publication. The live-refresh check proves the false-live profile is omitted
from local materialization and the live catalog while stale managed runtime
copies remain eligible for cleanup.
