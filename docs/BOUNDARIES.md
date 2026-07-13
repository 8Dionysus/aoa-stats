# Boundaries

## Purpose

This document keeps `aoa-stats` honest about what it may summarize and what it
must not pretend to own.

## Source ownership

- `aoa-skills` owns bounded workflow meaning
- `aoa-evals` owns bounded proof meaning
- `aoa-techniques` owns reusable practice meaning
- `aoa-playbooks` owns scenario composition
- `aoa-agents` owns role and checkpoint contract meaning
- `aoa-memo` owns memory and provenance-thread support surfaces
- `abyss-stack` owns runtime-local trial and closeout truth

## Stats posture

`aoa-stats` is derived.

It owns the shared statistical grammar, local-port compatibility, central
coverage inventory, deterministic cross-field semantics, and weaker derived
views. Each owner repository retains its measurement questions, object and
population meaning, dimensions, evidence, privacy posture, freshness, and
exports.

`aoa-stats` also owns the canonical shared receipt envelope and active
cross-repo event-kind vocabulary used by stats builders and live refresh.
Owner repos still own payload schemas and payload meaning inside that shared
envelope.

It may consume:

- source-owned receipts
- evidence refs
- bounded eval verdicts
- bounded progression deltas

It may emit:

- object summaries
- micro friction receipts, recurrence snapshots, and inbox summaries
- candidate-lineage summaries
- session-growth branch summaries
- supersession-drop summaries
- repeated-window summaries
- route-progression summaries
- fork-calibration summaries
- automation-pipeline summaries
- automation-followthrough summaries
- codex-plane deployment summaries
- reviewed memory movement summaries

It must not emit:

- one global quality score
- a replacement for bundle-local verdict meaning
- route or quest state authority
- workflow instructions that override owner repos
- durable memory truth or memory promotion decisions
- inboxes that pretend to be governance
- owner-local metric definitions authored centrally
- raw traces, raw session transcripts, or raw memory content
- MCP, routing, remediation, or runtime write commands

## Anti-collapse rules

- counts do not become proof
- proof does not collapse into one score
- progression stays bounded and multi-axis
- raw checkpoint notes stay out unless an owner-local reviewed receipt carries the needed lineage forward
- evidence stays linked rather than duplicated
- derived summaries stay weaker than owner-local meaning
- missing, unknown, stale, zero, fail, and partial remain distinct
- incompatible units, versions, populations, windows, or dimensions do not
  aggregate
- a local root `stats/` port does not transfer domain authority to
  `aoa-stats`
