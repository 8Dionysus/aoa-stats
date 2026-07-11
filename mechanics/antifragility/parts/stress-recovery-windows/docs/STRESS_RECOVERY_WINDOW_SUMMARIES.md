# Stress Recovery Window Summaries

## Current Surface

`aoa-stats` may derive bounded recovery-window observations from source-owned
receipts, bounded eval reports, and explicit adjacent-layer objects. This is a
derived view, not a new owner of meaning.

The current `stress_recovery_window_summary` profile is active as a public
contract but sets `live_state_capable: false`. Its committed output represents
a draft/example chain:

1. the stress-recovery receipt in
   `stats/intake-contract/examples/session_harvest_family.receipts.example.json`
2. the current committed `aoa-evals` example at
   `evals/comparison/longitudinal-window/aoa-stress-recovery-window/reports/example-report.json`
3. the derived public summary at
   `generated/stress_recovery_window_summary.min.json`

This chain demonstrates projection and suppression semantics. It does not
claim that a current owner producer or live repeated-window proof family
exists.

## Core And Source Boundary

`src/aoa_stats_builder/stress_recovery.py` owns the filesystem-free projection:

- selecting the latest relevant `aoa-stress-recovery-window` receipt
- counting bounded report inputs
- calculating `none`, `low_sample`, or `insufficient_evidence` suppression
- projecting the public summary without mutating its inputs

`src/aoa_stats_builder/stress_recovery_sources.py` owns filesystem translation:

- resolve only safe, exact `repo:aoa-evals/...` refs under the configured owner
  root
- return no report when an exact source is absent, malformed, outside the
  owner root, or belongs to another repository
- keep committed-reference compatibility separate from live resolution

The committed receipt retains the historical ref
`repo:aoa-evals/bundles/aoa-stress-recovery-window/reports/example-report.json`.
The explicitly named committed-reference loader may translate only that ref to
the current example location. `load_stress_recovery_report`, the ordinary exact
loader, never performs this alias and therefore cannot silently substitute an
example for missing live evidence.

## Why The Projection Exists

Wave 3 created objects that describe how stress moves:

- agent handoffs
- playbook lanes and re-entry gates
- projection health and regrounding tickets

Wave 4 needs a bounded way to answer:

- how often did a recovery path stay contained
- how often did route posture remain disciplined
- how often did re-entry stay evidence-backed
- how often did regrounding improve the derived surface without false promotion

`aoa-stats` may answer these as derived windows because it already owns machine-first summaries.

## Input Discipline

Preferred inputs:

1. source-owned owner receipts
2. bounded eval reports for the same family and window
3. explicit wave-3 objects cited by those reports
4. route hints and memo pattern objects only as secondary supporting material

A stats builder should refuse to derive a confident window from route hints or
memo objects alone. A missing or unreadable report yields
`suppression.status=insufficient_evidence`; a structurally valid but sparse
report yields `low_sample`. Neither state triggers fallback to a committed
example in the exact live adapter.

## Suggested Split Axes

A first window summary should keep explicit axes such as:

- `containment`
- `route_discipline`
- `reentry_quality`
- `regrounding_effectiveness`
- `evidence_continuity`
- `adaptation_followthrough`
- `operator_burden`
- `trust_calibration`

These are derived summary axes, not proof verdicts and not workflow meaning.

## Suppression Posture

When evidence is too thin, prefer:

- `suppression.status=low_sample`
- null values for weak axes
- an explicit reason

A cautious summary is healthier than a grand fiction.

## Publication Routes

The surface retains:

- one part-local supporting contract at
  `mechanics/antifragility/parts/stress-recovery-windows/schemas/stress_recovery_window_summary_v1.json`
- one generated repo surface at `generated/stress_recovery_window_summary.min.json`
- one bounded chaos-wave example at
  `mechanics/antifragility/parts/stress-recovery-windows/docs/STRESS_RECOVERY_SUMMARIES_CHAOS_WAVE1.md`
  and
  `mechanics/antifragility/parts/stress-recovery-windows/examples/stress_recovery_window_summary.chaos-wave1.example.json`

The generated surface stays downstream from `eval_result_receipt` envelopes
and their linked reports. The public schema and committed output remain stable
publication routes; part-local schemas and examples are supporting payload,
not stronger authority.

## Future Activation

The profile may become live-capable only after all of the following exist and
are tested together:

1. an activated `aoa-evals` Stress Recovery producer
2. current owner receipts carrying exact current report refs
3. a current report contract rather than a draft/example-only chain
4. a refresh observation route that notices both receipt and report movement
5. stale-output cleanup and focused live-refresh validation

These conditions are authoritative in
`docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md`.
Changing the adapter alone, or making the committed example readable, is not
live activation.
