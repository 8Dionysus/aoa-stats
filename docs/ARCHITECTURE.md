# Architecture

## One sentence

`aoa-stats` is an evidence-linked observability layer built from owner-local
receipts, bounded eval verdicts, and small progression deltas.

## Five layers

### 1. Event facts

Append-only receipts say what happened.

The canonical shared receipt envelope and active event family live in
`schemas/stats-event-envelope.schema.json`.
`aoa-stats` owns that shared input contract for cross-repo derivation only.
Owner repos still own the payload contracts that travel inside the envelope.

Examples:

- a harvest packet closed
- a fork was offered and one branch was chosen
- a repair cycle ended
- an automation candidate was detected
- one bounded eval publication happened
- one runtime wave closeout reached a gate and attempted a reviewed handoff

These are facts, not proof.

Corrections stay append-only too. If a newer receipt sets `supersedes`, the raw
log keeps both events while the active stats view collapses to the latest
resolvable correction inside the current feed.

### 2. Evidence links

Each receipt should point to inspectable artifacts through `evidence_refs`
instead of copying raw patches, logs, or reports.

### 3. Bounded evaluations

Quality enters through bounded eval verdicts and review surfaces.
`aoa-stats` may quote or summarize verdicts, but it must not replace them.

### 4. Progression readings

Progression stays route-scoped or quest-scoped and multi-axis.
The stats layer may accumulate deltas, cautions, holds, advances, reanchors,
and downgrades without pretending one total score explains everything.

### 5. Derived views

Derived views stay machine-first.

Current v0 derived views:

- core-skill-application summary
- object summary
- candidate-lineage summary
- owner-landing summary
- supersession-drop summary
- repeated-window summary
- route-progression summary
- fork-calibration summary
- automation-pipeline summary
- runtime-closeout summary
- surface-detection summary
- summary-surface catalog

`generated/summary_surface_catalog.min.json` is the compact owner-owned
runtime-entry capsule for `aoa-stats`. It points back to derived view families
without replacing the underlying receipts or owner-local authority.

`generated/candidate_lineage_summary.min.json` is the first growth-refinery
funnel slice. It reads reviewed owner-local lineage entries only and does not
pull raw checkpoint carry into stats.

`generated/owner_landing_summary.min.json` and
`generated/supersession_drop_summary.min.json` are the next bounded
growth-refinery followthrough slices. They read reviewed owner landing bundles,
seed-owner landing traces, and explicit reviewed turnover signals without
claiming owner truth.

The published runtime-entry capsule is the schema-backed v2 contract:

- `schema_version`
- `schema_ref`
- `owner_repo`
- `surface_kind`
- `authority_ref`
- `generated_from`
- `validation_refs`
- `surfaces`

Each entry in `surfaces` stays compact and low-context:

- `name`
- `surface_ref`
- `schema_ref`
- `primary_question`
- `derivation_rule`

## Canonical split

- counts answer: how often and how widely
- kernel usage answers: which project-core skills are really finishing and with which bounded detail receipts
- verdicts answer: how well on one bounded surface
- progression answers: what changed on named axes
- evidence refs answer: where to inspect next

`object_summary`, `repeated_window_summary`, and
`surface_detection_summary` are inclusive of active receipts only, not of
superseded raw history.
