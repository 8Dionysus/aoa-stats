# Continuity Window Summary

## Purpose

`aoa-stats` exposes one bounded self-agency continuity companion:

- `generated/continuity_window_summary.min.json`

This surface exists to make the current continuity window legible without
turning stats into continuity truth, playbook authority, memory authority, or
self-agency proof.

## Current v1 source chain

The first slice is a static derived snapshot, not a live receipt family.

It reads:

- the public continuity window example in `aoa-agents`
- the sovereign recurring route in `aoa-playbooks`
- the memo-side provenance thread example in `aoa-memo`
- the landed continuity proof anchors in `aoa-evals`

That keeps the summary downstream of owner-owned continuity surfaces until
reviewed live continuity receipts exist.

## Minimal fields

- `continuity_ref`
- `current_status`
- `open_revision_windows`
- `successful_reanchors`
- `failed_reanchors`
- `last_anchor_artifact_ref`
- `drift_flags`
- `bounded_revision_count`

## Negative rules

Do not:

- let this summary authorize a continuity claim
- infer hidden runtime autonomy from an open continuity window
- replace the active revision window with a stats snapshot
- replace memo provenance, playbook route truth, or eval proof
- widen this surface into a universal self-agency score

## One-line rule

The summary describes the current bounded continuity posture.
It does not decide whether continuity is legitimate.
