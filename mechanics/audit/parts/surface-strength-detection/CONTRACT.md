# Surface-strength detection contract

## Input and derivation

- Consume only active finish-stage `core_skill_application_receipt` events
  admitted by the shared live receipt route.
- Group every admitted finish-stage receipt by its observed date. Missing,
  non-mapping, or empty `surface_detection_context` becomes an empty context
  and enters the legacy `activated` compatibility bucket.
- Preserve candidate-count coercion as `int(value or 0)`. Upstream payloads
  must therefore provide values accepted by that legacy conversion; this core
  does not add stricter payload validation during extraction.
- Report `first_observed_at` and `last_observed_at` from the first and last
  admitted receipt in supplied order within each date window.

## Output and compatibility

- Publish `generated/surface_detection_summary.min.json` against
  `schemas/surface-detection-summary.schema.json`.
- `src/aoa_stats_builder/core_skill_observation.py` owns the deterministic
  derivation shared with `core-skill-application`.
- `scripts/build_views.py` retains the historical helper and builder names as
  compatibility aliases plus repo-wide fan-out; it does not own duplicate
  derivation logic.

## Authority stop-line

Detection context remains an advisory fact authored by the receipt owner.
The legacy `activated` bucket can also contain receipts with no owner-authored
context, so it must never be read as owner activation truth. aoa-stats may
preserve and summarize the compatibility projection but cannot strengthen the
source claim, select a route, or issue proof, gate, workflow, or
surface-ownership truth.

The context bucket, integer coercion, and supplied-order bounds are explicit
compatibility debt. Correcting them is a separate behavior-changing cycle with
public-output review, not part of this extraction.
