# AOST-D-0007 Titan Reference Rosters Are Not Observed Swarm Activity

## Index Metadata

- Decision ID: AOST-D-0007
- Original date: 2026-07-11
- Surface classes: stats/read-models, mechanics/titan, src/projection, generated/read-models
- Stats surfaces: Titan Incarnation, Titan Summon, summary surface catalog
- Source lanes: aoa-agents Titan rosters, aoa-sdk incarnation receipt examples, aoa-sdk swarm-ledger contract
- Guard families: derived-only authority, reference-source posture, cross-owner coherence, missing-evidence visibility, zero-baseline interpretation, live-source admission
- Posture: accepted

## Status

Accepted

## Context

The root builder historically returned fixed Titan Incarnation counts of five
seeded Titans, three default-active Titans, and two gate-locked Titans. It
cited `seed:titan-fifteenth-wave`, although no corresponding manifest is
present in the tracked 8Dionysus owner surfaces.

The same 5/3/2 partition is present in three exact checked-in owner examples:
the `aoa-agents` operator-console roster, the `aoa-agents` runtime roster, and
the `aoa-sdk` v2 Titan session receipt. They agree on the five Titan names,
the active/locked partition, and the `mutation` and `judgment` gates. Those
files are examples, not current owner-runtime incarnation state.

The root Titan Summon builder separately returned four zero counts and cited
`seed:titan-sixteenth-wave`. No corresponding manifest, committed swarm-ledger
instance, or closeout receipt was found. `aoa-sdk` owns a ledger schema and
helper, but a helper that can initialize empty arrays is not evidence that a
real swarm ran and produced zero tasks, reports, findings, or memory
candidates. The old output therefore collapsed missing observation into zero.

## Decision

Titan Incarnation becomes a committed-reference projection of the exact three
owner examples. A source adapter loads those files, and a filesystem-free core
must validate identity, active/locked, and gate coherence before deriving the
counts. The legacy `source_receipt_refs` field remains for public-schema
compatibility but carries the exact owner-example paths. The surface remains
`live_state_capable: false`.

Titan Summon v1 remains as a compatibility surface, but its summary and source
identifiers explicitly say `no-observed-ledger`. Its four zero counts mean no
owner ledger was projected; they do not describe observed swarm activity. The
builder accepts no ledger input and must not infer activity from roster or
helper defaults. A future observed summary requires an owner-local ledger or
closeout artifact, a refresh route, and explicit review of whether the v1
shape should evolve, be superseded, or be retired.

Both root builder names remain thin compatibility and fan-out facades. Focused
behavioral proof lives with `mechanics/titan/parts/incarnation-summon`, while
source-authored questions and authority ceilings remain under
`stats/read-models/`.

## Options Considered

- Keep both hardcoded seed summaries unchanged: rejected because the symbolic
  wave references do not resolve to the actual owner evidence and the summon
  zeros masquerade as observations.
- Treat the empty arrays created by the SDK helper as an observed swarm
  ledger: rejected because executable defaults are a contract, not a recorded
  owner event.
- Derive summon activity from the roster or session-receipt example: rejected
  because incarnation state does not prove that agents were invoked or that
  reports, findings, or memory candidates existed.
- Remove Titan Summon immediately: rejected for this mechanics-led slice
  because removing an active public profile requires an explicit
  retired-output cleanup lifecycle and consumer review.
- Preserve the public v1 shape with an explicit no-ledger sentinel: chosen as
  the smallest honest compatibility boundary while the stats-led lifecycle
  question remains open.

## Rationale

`aoa-agents` owns Titan identity, roster, and gate meaning. `aoa-sdk` owns the
runtime helper and swarm-ledger transport contracts. `aoa-stats` may validate
and project a weaker committed example chain, but it cannot turn examples into
live incarnations or turn the absence of a ledger into a fact about activity.

Making the Incarnation chain exact and executable prevents its counts from
drifting away from the owners. Making the Summon baseline self-identifying
keeps compatibility without sacrificing the repository rule that missing
evidence must remain visible rather than becoming zero, success, or absence.

## Consequences

- Titan Incarnation retains its 5/3/2 counts but changes its summary and source
  references from a symbolic wave seed to exact committed-reference routes.
- Titan Summon retains four compatibility zero values but changes its summary
  and source identifiers to the explicit no-observed-ledger sentinel.
- Both public payload bytes and the generated catalog prose change
  intentionally; schemas and generated file paths remain stable.
- The Titan mechanic gains part-local cross-owner coherence, permutation,
  rejection, non-mutation, schema, facade, and committed-output tests.
- Neither surface enters local live materialization. Future activation must
  prove a current owner producer and an observation trigger together.
- Consumer re-grounding must prefer the exact owner paths and must disclose
  that the Summon surface is a compatibility baseline, not swarm evidence.

## Source Surfaces

- `AGENTS.md`
- `DESIGN.md`
- `stats/read-models/active/titan_incarnation_summary.profile.json`
- `stats/read-models/active/titan_summon_summary.profile.json`
- `stats/source_home.manifest.json`
- `src/aoa_stats_builder/titan_observation.py`
- `src/aoa_stats_builder/titan_observation_sources.py`
- `scripts/build_views.py`
- `schemas/titan_incarnation_summary.schema.json`
- `schemas/titan_summon_summary.schema.json`
- `generated/titan_incarnation_summary.min.json`
- `generated/titan_summon_summary.min.json`
- `mechanics/titan/parts/incarnation-summon/`
- `aoa-agents/mechanics/titan/parts/incarnation-spine/examples/operator-console-roster.v0.json`
- `aoa-agents/mechanics/titan/parts/runtime-roster/examples/runtime-roster.v0.json`
- `aoa-sdk/mechanics/titan/parts/incarnation-identity-runtime-helper-contracts/examples/titan_session_receipt.v2.example.json`
- `aoa-sdk/mechanics/titan/parts/swarm-ledger-closeout-helper-contracts/schemas/titan_swarm_ledger.schema.json`

## Validation

Run:

```bash
python scripts/generate_decision_indexes.py
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
python scripts/validate_mechanics_topology.py
python scripts/validate_stats_source_home.py
python scripts/build_views.py --check
python -m pytest -q mechanics/titan/parts/incarnation-summon/tests tests/test_build_views.py tests/test_summary_surface_catalog.py
python scripts/release_check.py
```
