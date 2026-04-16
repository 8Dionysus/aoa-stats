# Stress Recovery Window Summaries

## What This Surface Is

`aoa-stats` may derive repeated-window recovery summaries from source-owned receipts, bounded eval reports, and explicit adjacent-layer objects.

This is a **derived view**, not a new owner of meaning.

## Why Wave 4 Needs This

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

A stats builder should refuse to derive a confident window from route hints or memo objects alone.

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

## Output Posture

Wave 4 lands both:

- one public contract at `schemas/stress_recovery_window_summary_v1.json`
- one generated repo surface at `generated/stress_recovery_window_summary.min.json`
- one bounded chaos-wave example at
  `docs/STRESS_RECOVERY_SUMMARIES_CHAOS_WAVE1.md` and
  `examples/stress_recovery_window_summary.chaos-wave1.example.json`

The generated surface stays downstream from `eval_result_receipt` envelopes and their linked reports.
