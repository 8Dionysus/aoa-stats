# Continuity Window Summary

## Purpose

`aoa-stats` exposes one bounded self-agency continuity companion:

- `generated/continuity_window_summary.min.json`

This surface exists to make one represented continuity reference chain legible
without turning stats into current continuity truth, playbook authority,
memory authority, or self-agency proof.

## Current v1 source chain

The v1 slice is a static committed reference snapshot, not a live receipt
family and not evidence that the represented route occurred in this workspace.

It reads:

- the public continuity window example in `aoa-agents`
- the owner-authored experimental continuity route in `aoa-playbooks`
- the memo-side provenance thread example in `aoa-memo`
- the three draft continuity eval definitions in the `aoa-evals` catalog

The reference adapter loads those four surfaces and passes an immutable bundle
through a filesystem-free validator/projection core. It does not read the
advisory `aoa-sdk` closeout continuity hint: that example carries weaker,
different refs and cannot complete this owner chain.

The validator requires the continuity, revision, reanchor, and anchor refs to
match between `aoa-agents` and `aoa-memo`; enforces the exact owner-window v1
shape and meaningful memo source refs; verifies ordered timeline timestamps,
playbook contract tokens, catalog version 1, and the draft posture of all three
eval definitions; and derives reanchor counts only from the bounded explicit
action grammar. `continuity_status: reanchored` alone, ambiguous prose, and a
negated action are never success evidence.

That keeps the summary downstream of owner-owned continuity surfaces until a
canonical owner-runtime continuity artifact or receipt exists. The authored
profile is therefore not live-capable, and local live refresh must preserve
absence rather than replay these examples under `state/generated/`.

Future activation is intentionally stricter than replacing `.example.json`
with another path. A live artifact must carry timestamped workspace/session/run
identity, resolve the named anchor, and provide explicit decision/outcome
evidence for any reanchor count. A claimed `AOA-P-0029` route also needs a real
gate verdict and active composition; proof claims need real eval reports, and a
memo-backed projection needs reviewed runtime writeback. The SDK hint may be
checked optionally for drift, but cannot admit or complete the chain.

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

- let this summary authorize or claim current continuity
- infer hidden runtime autonomy from an open continuity window
- replace the active revision window with a stats snapshot
- replace memo provenance, playbook route truth, or eval proof
- widen this surface into a universal self-agency score

## One-line rule

The summary describes the bounded posture represented by its committed
reference chain. It does not decide whether continuity is current or
legitimate.
