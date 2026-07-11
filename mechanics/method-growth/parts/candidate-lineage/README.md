# candidate-lineage

Summarizes reviewed `candidate_lineage_entries` from
`harvest_packet_receipt` payloads into stage, owner-target, posture, misroute,
supersession, axis-pressure, and time-to-stage observations.

The authored meaning lives in
`stats/read-models/active/candidate_lineage_summary.profile.json`; the stable
public contract and output remain
`schemas/candidate_lineage_summary.schema.json` and
`generated/candidate_lineage_summary.min.json`. Deterministic projection is
shared with the other Method Growth parts through
`src/aoa_stats_builder/candidate_lifecycle.py`.
