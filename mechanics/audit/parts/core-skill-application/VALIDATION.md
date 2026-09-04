# Validation

This part adds no independent executable check. Use the
[Audit shared-core route](../../VALIDATION.md). Use
[shared repository checks](../../../../VALIDATION.md#shared-repository-checks)
only when the wider repository surface is in scope.

The package-level test is intentional: it covers the core shared with
`surface-strength-detection`, finish-stage filtering, deterministic grouping,
the root compatibility aliases, schema validity, and committed-output parity.
The root tests retain repo-wide orchestration and public-route coverage.
