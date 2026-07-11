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
