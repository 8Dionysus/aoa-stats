# Architecture

## One sentence

`aoa-stats` is an evidence-linked observability layer built from owner-local
receipts, bounded eval verdicts, and small progression deltas.

## Five layers

### 1. Event facts

Append-only receipts say what happened.

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
- repeated-window summary
- route-progression summary
- fork-calibration summary
- automation-pipeline summary
- runtime-closeout summary

## Canonical split

- counts answer: how often and how widely
- kernel usage answers: which project-core skills are really finishing and with which bounded detail receipts
- verdicts answer: how well on one bounded surface
- progression answers: what changed on named axes
- evidence refs answer: where to inspect next

`object_summary` and `repeated_window_summary` are inclusive of active receipts
only, not of superseded raw history.
