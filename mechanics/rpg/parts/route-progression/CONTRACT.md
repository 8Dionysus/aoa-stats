# Route Progression contract

## Owner chain

- `Agents-of-Abyss/mechanics/rpg` owns progression-reading vocabulary and
  authority stop-lines.
- `aoa-skills` owns admitted `progression_delta_receipt` payload facts.
  Consumer re-grounding starts at its tracked current semantic schema and
  semantic example, not at the legacy numeric compatibility fixture.
- `aoa-agents/mechanics/rpg/parts/progression-model/` owns the agent-layer
  seven-axis progression overlay.
- `aoa-sdk` RPG models and checkpoint-carry contracts own typed consumer and
  transport expectations.
- `stats/read-models/active/route_progression_summary.profile.json` owns only
  the bounded stats question, input posture, public routes, and authority
  ceiling. This part owns its repeatable projection route.

## Fixed projection vocabulary

The core aggregates exactly these seven axes:

1. `boundary_integrity`
2. `execution_reliability`
3. `change_legibility`
4. `review_sharpness`
5. `proof_discipline`
6. `provenance_hygiene`
7. `deep_readiness`

Unknown axes do not enter the public summary. A cumulative total is a bounded
receipt observation, not rank, mastery, unlock, navigation, agent progression,
or a route decision.

## Reference input boundary

The active public surface is a committed legacy numeric snapshot. The current
owner contract uses semantic `scope_ref`, `axis_delta_summary`, and
`caution_refs` fields and explicitly avoids a score-shaped model. When a
receipt supplies semantic `axis_delta_summary` without numeric `axis_deltas`,
the core fails explicitly. It must never translate posture labels into numbers.

The exact first owner-return refs are
`aoa-skills/skills/core/session-growth/aoa-session-progression-lift/references/progression-delta-receipt-schema.yaml`
and
`aoa-skills/mechanics/growth-cycle/examples/session-growth-artifacts/progression_delta_receipt.kernel-maturity.json`.
They describe current semantic truth; they do not change the committed numeric
projection ABI.

Route Progression is therefore `live_state_capable: false`. Live refresh omits
the builder, removes a stale managed output, and does not advertise the surface
until a cross-owner semantic projection contract exists.

## Extraction compatibility

- Only exact `progression_delta_receipt` events are admitted by the core.
- A falsey payload `route_ref` falls back to `session_ref`.
- Axis values pass through Python's `isinstance(value, int)` rule; booleans
  therefore retain their historical integer behavior, and other values are
  ignored.
- `caution_count` is the length of each list-valued `cautions` payload; member
  shape is not revalidated by this projection, and non-lists add nothing.
- The latest receipt is selected by maximum `(observed_at, event_id)`.
- An absent, empty, or non-string latest `verdict` becomes `"unknown"`, keeping
  every successful output within the public schema.
- Input receipts and the supplied `generated_from` object are not mutated.

## Output and facade

- Publish `generated/route_progression_summary.min.json` against
  `schemas/route-progression-summary.schema.json`.
- `src/aoa_stats_builder/route_progression.py` is the sole deterministic core.
- `scripts/build_views.py` retains historical names as compatibility aliases
  and performs repo-wide input resolution and output fan-out only.

## Behavior-change stop-line

The compatibility rules above describe the current extraction target; they do
not authorize malformed owner payloads or redefine stronger RPG contracts.
Normalizing falsey route refs, excluding booleans, validating caution members,
or changing legacy numeric accumulation is a separate behavior change that
must review the receipt contract, public schema/output bytes, consumers, and
reference projection. Live activation additionally requires a non-invented
contract for the semantic owner shape.
