# Consumer regrounding validation

## Current focused checks

Run from the repository root:

```bash
python -m pytest -q \
  mechanics/boundary-bridge/parts/consumer-regrounding/tests/test_consumer_regrounding_signals.py
```

See [Shared repository checks](../../../../VALIDATION.md#shared-repository-checks) for this repository-wide check.

These checks constrain catalog shape, owner-truth references, authority
ceilings, derived-signal precedence, and the consumer meaning of intake-coverage
signals. Producer aggregation invariants and committed Source Coverage parity
are verified under `mechanics/audit/parts/source-coverage/tests/`.

The topology validator additionally proves that the focused test is part-local
and only declared public/compatibility routes remain at root.
