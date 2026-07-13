# AOST-D-0005 Route Progression Semantic Receipts Are Not Numeric Live State

## Index Metadata

- Decision ID: AOST-D-0005
- Original date: 2026-07-11
- Surface classes: stats/read-models, mechanics/rpg, mechanics/recurrence, src/projection, state/generated, consumer-regrounding
- Stats surfaces: Route Progression, live summary catalog
- Source lanes: aoa-skills progression receipts, Agents-of-Abyss RPG center, aoa-agents agent progression, aoa-sdk stats contracts
- Guard families: derived-only authority, live-source admission, owner-contract compatibility, schema-output parity, stale-output cleanup, consumer regrounding
- Posture: accepted

## Status

Accepted

## Context

The committed Route Progression summary was built from an older numeric
`progression_delta_receipt` shape: `route_ref`, `axis_deltas`, and `cautions`.
The current `aoa-skills` owner contract instead requires `scope_ref`,
`axis_delta_summary`, `axis_evidence_posture`, and optional `caution_refs`.
That contract deliberately keeps movement descriptive rather than
score-shaped.

The live receipt corpus contains both shapes. The legacy builder silently
grouped semantic-only receipts under `session_ref`, emitted zero for every
axis, and ignored their caution refs. Keeping the profile live-admitted would
therefore advertise a numeric surface that does not faithfully represent the
current owner contract. Mapping labels such as `advance`, `hold`, or
`thin-evidence` to integers inside aoa-stats would invent progression meaning
that the owner explicitly did not authorize.

The same audit found that a present null or otherwise non-string verdict could
escape the builder even though the public schema and `aoa-sdk` stats model
require a non-empty string.

## Decision

Route Progression remains an active committed compatibility surface, but its
profile becomes reference-only. The committed projection continues to use the
legacy numeric receipt fixture and preserves its public payload bytes. The
live refresh path must not invoke or publish this builder and must remove a
stale managed runtime copy if one exists.

The RPG core rejects semantic-only `axis_delta_summary` receipts when no
numeric `axis_deltas` mapping is supplied; it never assigns numeric values to
owner-authored posture labels. Successful projections normalize a missing,
empty, or non-string latest verdict to `unknown` so the public output always
meets its schema.

Future live activation requires an explicit cross-owner projection contract
that can represent the current semantic receipt shape without manufacturing a
score. That may require a new or widened public schema; merely making the old
builder accept the field names is insufficient.

## Options Considered

- Map semantic posture labels to integer deltas in aoa-stats: rejected because
  the owner contract is intentionally descriptive and stats does not own the
  scoring law.
- Keep the profile live and count semantic-only receipts as zero movement:
  rejected because zero is an invented observation, not faithful absence.
- Remove Route Progression entirely: rejected because the committed numeric
  compatibility snapshot and stable public contract remain useful.
- Keep the surface active but reference-only until an owner-approved semantic
  projection exists: chosen because it preserves compatibility without making
  a false currentness or scoring claim.

## Rationale

AoA observability is useful only while it remains weaker than owner meaning.
The RPG center owns progression-reading vocabulary and stop-lines;
`aoa-agents` owns the agent-layer progression overlay; `aoa-sdk` owns typed
transport and consumer contracts; and `aoa-skills` owns the receipt payload.
aoa-stats may project a contract shared by those owners, but it may not infer a
numeric scale from semantic posture words.

Reference-only posture makes the incompatibility visible and reversible. It
also keeps the legacy projection available while preventing mixed live inputs
from being summarized as if they shared one numeric ABI.

## Consequences

- The managed inventory remains 25 active profiles; 12 are live-admitted and
  13 are committed/reference-only.
- `generated/route_progression_summary.min.json` keeps its existing schema and
  bytes for the committed fixture.
- Route Progression is omitted from the live catalog and stale runtime copies
  are cleaned.
- Semantic-only current owner receipts fail explicitly if passed to the legacy
  numeric core; they are not reduced to zero or assigned a score.
- Every successful core result has a schema-valid non-empty string
  `latest_verdict`.
- Consumer regrounding must return the surface to the RPG center and named
  stronger owners rather than to aoa-stats.

## Source Surfaces

- `stats/read-models/active/route_progression_summary.profile.json`
- `stats/intake-contract/event-kind-registry.json`
- `stats/source_home.manifest.json`
- `src/aoa_stats_builder/route_progression.py`
- `schemas/route-progression-summary.schema.json`
- `scripts/build_views.py`
- `mechanics/rpg/parts/route-progression/`
- `mechanics/recurrence/parts/live-receipt-refresh/scripts/refresh_live_stats.py`
- `mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py`
- `aoa-skills/skills/core/session-growth/aoa-session-progression-lift/references/progression-delta-receipt-schema.yaml`
- `Agents-of-Abyss/mechanics/rpg/README.md`
- `aoa-agents/mechanics/rpg/parts/progression-model/`
- `aoa-sdk/src/aoa_sdk/contracts/stats.py`

## Validation

Decision-lane checks are owned by [`AGENTS.md#verify`](AGENTS.md#verify).
Affected source-home and mechanic checks route through their owning
`AGENTS.md` or `VALIDATION.md`, then the root
[`AGENTS.md#verify`](../../AGENTS.md#verify) gate.
