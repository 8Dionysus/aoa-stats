# Validation

This part adds no independent executable check. Use the
[Audit shared-core route](../../VALIDATION.md). Use
[shared repository checks](../../../../VALIDATION.md#shared-repository-checks)
only when the wider repository surface is in scope.

The package-level test is intentional: it covers the core shared with
`core-skill-application`, finish-stage selection, the legacy missing-context
`activated` bucket, supplied-order date-window bounds, advisory counters,
non-mutating projection, root compatibility aliases, schema validity, and
committed-output parity. It preserves extraction compatibility; it does not
prove owner activation or strict candidate-count payload validation.
