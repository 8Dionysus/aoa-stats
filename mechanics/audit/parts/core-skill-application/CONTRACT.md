# Core-skill application contract

## Input and derivation

- Consume only active `core_skill_application_receipt` events admitted by the
  shared live receipt route.
- Count only receipts whose application stage is `finish`.
- Group by the receipt-backed kernel and skill identity; missing identity is
  handled by the bounded compatibility fallback, not by external lookup.
- Select recency deterministically from `observed_at` and `event_id`, so input
  order cannot change the published view.

## Output and compatibility

- Publish `generated/core_skill_application_summary.min.json` against
  `schemas/core-skill-application-summary.schema.json`.
- `src/aoa_stats_builder/core_skill_observation.py` owns the deterministic
  derivation shared with `surface-strength-detection`.
- `scripts/build_views.py` retains the historical helper and builder names as
  compatibility aliases plus repo-wide fan-out; it does not own duplicate
  derivation logic.

## Authority stop-line

The input receipt owners retain application, skill, kernel, and workflow
truth. A counted finish-stage receipt is an observation of a receipt, not
proof of skill quality, successful owner landing, workflow completion, or a
routing/gate verdict. aoa-stats must not repair or enrich missing owner facts.
