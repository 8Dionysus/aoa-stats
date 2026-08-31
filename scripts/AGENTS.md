# AGENTS.md

## Local role

Root scripts are public, compatibility, or repository-wide entrypoints. They
adapt inputs, call source-owned builders and validators, and keep I/O, fan-out,
and check/write policy at the edge. Reusable deterministic logic belongs in
`src/aoa_stats_builder/` or the owning mechanic part.

## Editing posture

Preserve explicit source-root precedence, owner attribution, missingness, and
derived-only output posture. Builders read authored inputs and write declared
projections; validators check their stated contract and cannot strengthen an
upstream verdict. Live-refresh scripts require explicit operator intent and
must not silently mutate sibling repositories.

`build_views.py` remains the compatibility build facade. `release_check.py`
retains the complete ordered owner-local gate. Exact command sequences belong
to the root or nearest `VALIDATION.md`, not this inherited card.

## Hard no

Do not add hidden fallback paths, private credentials, ambient runtime state,
central proof or health authority, or a second source-family or topology
inventory. Do not treat a green script as CI, review, merge, runtime, or owner
acceptance evidence.

## Conditional validation and closeout

Open root `VALIDATION.md` for repository script checks and the named mechanic
part route for moved builders or validators. Report the script surface, source
inputs, projection outputs, checks actually run, generated parity, and any
external or runtime evidence that remains missing.
