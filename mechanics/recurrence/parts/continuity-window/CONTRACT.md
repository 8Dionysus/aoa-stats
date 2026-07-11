# Continuity window contract

## Purpose

Produce one deterministic, derived-only committed reference posture from an
explicit owner-authored continuity, playbook, memory, and eval example chain.

## Inputs

- the authored `continuity_window_summary` profile under `stats/read-models/`
- the public `aoa-agents` Continuity Window example
- the experimental `aoa-playbooks` continuity route
- the `aoa-memo` continuity provenance-thread example
- the `aoa-evals` catalog entries for the three named continuity eval anchors
- this part's bounded example and guide

## Output

`generated/continuity_window_summary.min.json`, validated by
`schemas/continuity-window-summary.schema.json`.

## Adapter boundary

- `continuity_window_sources.py` owns environment/path discovery, fallback
  resolution for known historical memo placement, source loading, and
  construction of the immutable committed-reference bundle
- filesystem-free `continuity_window.py` owns source-chain validation,
  coherence rules, evidence-backed counting, and deterministic projection
- `scripts/build_views.py` preserves the zero-argument compatibility facade and
  repo-wide fan-out only
- the advisory `aoa-sdk` continuity-hint example is not an input: its refs do
  not identify this public owner chain and it cannot mint continuity truth

## Invariants

- an open window does not authorize a continuity claim
- the summary cannot replace a revision window or memory provenance
- counts do not imply hidden runtime autonomy or self-agency proof
- missing owner evidence remains visible rather than becoming success
- `continuity_ref`, `revision_window_ref`, `reanchor_ref`, and
  `anchor_artifact_ref` remain coherent between `aoa-agents` and `aoa-memo`
- the `aoa-agents` object keeps the exact published v1 field shape, including
  `notes` only as string or null, and memo source refs name the relevant owner
  surfaces rather than merely an owner repository
- the eval catalog remains version 1 and the three consumed entries remain
  `draft`; promotion is a contract review event, not an implicit stronger claim
- `continuity_status` is route posture, not a completed reanchor receipt
- successful and failed reanchor counts come only from explicit ordered memo
  timeline actions in the bounded action grammar; status alone and ambiguous
  prose never increment either count
- invalid or unordered timestamps, missing playbook anchors, and missing eval
  anchors fail the committed reference build
- live refresh must not invoke this reference adapter or fall back to examples

## Live activation boundary

Future live activation requires a canonical owner-runtime continuity artifact
or receipt that names the continuity, revision, reanchor, and anchor chain and
provides explicit occurrence evidence for any reanchor count. Introducing that
source contract or adding it to the shared stats receipt ABI is a separate
owner decision.

The runtime artifact must be non-example, timestamped, scoped to an explicit
workspace/session/run identity, and resolve its anchor artifact. If it claims
the `AOA-P-0029` route, the playbook must have a real gate verdict and active
composition; any proof claim must cite real eval reports rather than draft eval
definitions. Memo is optional unless the projection consumes memo-backed
fields, in which case it must be a reviewed runtime writeback or receipt. An
SDK continuity hint may be optional consistency evidence only and never
activation authority.

## Crosswalk

This part operates on stats source-family id `read_models`. The source profile
owns meaning; this part owns the recurring continuity-window derivation route.
