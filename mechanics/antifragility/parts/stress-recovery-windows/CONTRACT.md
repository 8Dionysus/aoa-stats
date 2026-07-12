# Contract

## Ownership

- `aoa-evals` retains eval receipt, report, verdict, and proof authority.
- `stats/read-models/active/stress_recovery_window_summary.profile.json` owns
  the bounded derived question and declares the current false-live posture.
- This part owns the Stress Recovery operation route and focused validation;
  the root schema and generated summary remain stable public publication
  routes.

## Implementation boundary

- `src/aoa_stats_builder/stress_recovery.py` is a pure projection core. It may
  select the latest relevant receipt, calculate suppression, and project the
  summary, but it must not read paths, inspect environment variables, or load
  files.
- `src/aoa_stats_builder/stress_recovery_sources.py` is the source adapter. Its
  ordinary loader resolves only a safe, exact `repo:aoa-evals/...` reference
  beneath the configured `aoa-evals` root.
- The committed fixture names the canonical report ref
  `repo:aoa-evals/evals/comparison/longitudinal-window/aoa-stress-recovery-window/reports/example-report.json`.
  Committed and live-facing builds use the same exact loader; no retired
  bundle-path alias or missing-source fallback is part of the adapter contract.
- Missing, malformed, or structurally incomplete reports produce an explicit
  `insufficient_evidence` projection; they do not authorize example fallback
  or a stronger claim.

## Current and future posture

The committed summary is a draft/example read model and
`live_state_capable: false`. It remains weaker than owner receipts and eval
reports and never becomes proof, routing, gate, identity, or workflow truth.

Live activation requires all conditions named by AOST-D-0004: an
activated owner eval producer, a current report contract, and a refresh-observed
receipt/report chain. A readable committed example alone is not sufficient.
