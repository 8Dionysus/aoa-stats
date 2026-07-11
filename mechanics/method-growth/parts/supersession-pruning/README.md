# supersession-pruning

Summarizes explicit drop, replacement, merge, supersession, and reanchor
signals across reviewed candidate lineage, reviewed owner landing, and seed
landing trace receipts.

The authored meaning lives in
`stats/read-models/active/supersession_drop_summary.profile.json`; the stable
public contract and output remain
`schemas/supersession-drop-summary.schema.json` and
`generated/supersession_drop_summary.min.json`. Deterministic projection is
shared through `src/aoa_stats_builder/candidate_lifecycle.py`.

The shared core retains normalization for `reviewed_owner_landing_receipt` and
`seed_owner_landing_trace_receipt` because their explicit turnover fields feed
this active surface. That does not reactivate the retired standalone
`owner_landing_summary` or make committed landing examples current owner fact.

Focused schema, permutation, non-mutation, active-receipt stability, and
explicit-turnover proof lives in `tests/test_supersession_pruning.py`.
