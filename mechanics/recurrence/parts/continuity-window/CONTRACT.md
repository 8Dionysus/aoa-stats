# Continuity window contract

## Purpose

Produce one deterministic, derived-only continuity posture from explicit
owner-authored continuity, playbook, memory, and eval references.

## Inputs

- the authored `continuity_window_summary` profile under `stats/read-models/`
- owner-authored continuity surfaces named by the shared builder
- this part's bounded example and guide

## Output

`generated/continuity_window_summary.min.json`, validated by
`schemas/continuity-window-summary.schema.json`.

## Invariants

- an open window does not authorize a continuity claim
- the summary cannot replace a revision window or memory provenance
- counts do not imply hidden runtime autonomy or self-agency proof
- missing owner evidence remains visible rather than becoming success

## Crosswalk

This part operates on stats source-family id `read_models`. The source profile
owns meaning; this part owns the recurring continuity-window derivation route.
