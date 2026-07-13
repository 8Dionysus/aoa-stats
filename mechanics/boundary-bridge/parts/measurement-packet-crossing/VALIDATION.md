# Measurement packet crossing validation

Focused semantic proof lives in this part's `tests/` district. Schema,
inventory, and optional local-port validation are owned by
`scripts/validate_stats_protocol.py`. The repository-wide executable route is
`scripts/release_check.py`.

The proof covers the invariants named in `CONTRACT.md`, including negative
cases that reject false aggregation and false live or privacy posture.
