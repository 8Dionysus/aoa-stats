# Memory Movement Summary

## Purpose

`generated/memory_movement_summary.min.json` is the derived stats view for the
committed `aoa-memo` reviewed-corpus snapshot and reviewed-intake landing
movement.

It answers: how many reviewed corpus objects exist, which kinds and recall
postures they carry, what KAG-lift posture is visible, and what reviewed-intake
packets have landed.

It does not claim that the snapshot is continuously current in local live
state. The active profile is reference-only until the complete source contract
has a tested observation route.

## Authority map

- `aoa-memo` owns the reviewed corpus, catalog source material, reviewed
  intake, landing receipts, and memory meaning.
- `stats/read-models/active/memory_movement_summary.profile.json` owns the
  stats question, input posture, authority ceiling, and live-admission bit.
- `mechanics/boundary-bridge/parts/memory-owner-handoff/CONTRACT.md` owns this
  repeatable crossing contract.
- `src/aoa_stats_builder/memory_movement.py` owns deterministic projection
  rules only.
- `src/aoa_stats_builder/memory_movement_sources.py` owns filesystem and source
  adaptation only.
- `scripts/build_views.py` is the stable root compatibility, CLI, and
  publication facade.
- `generated/memory_movement_summary.min.json` is a committed derived
  companion; `state/generated/` is operational live state and currently must
  not contain this surface.

## Exact inputs

The source adapter reads exactly four `aoa-memo` roots:

- `generated/memory-objects/memory_object_catalog.min.json`
- `memo/objects/**/object.json`
- `memo/intake/reviewed/*.json`
- `memo/intake/receipts/*.json`

There is no fallback to a teaching fixture, example bundle, history snapshot,
or alternate topology. The generated catalog may contain rows marked
`teaching_fixture`; those rows remain visibly classified and contribute only
to `source_kind_counts`. Reviewed lifecycle and landing observations come from
the reviewed owner roots.

The adapter recursively discovers `memo/objects/**/object.json` in sorted path
order and discovers reviewed-intake and landing JSON files directly, also in
sorted order. It converts concrete paths into `aoa-memo/...` logical refs and
returns a deeply frozen `MemoryMovementInputBundle`.

## Core and adapter contract

The pure projection core receives only mappings, sequences, and logical repo
refs. It performs no path resolution, environment lookup, file reading, or
JSON loading. It:

1. checks `source_of_truth=aoa-memo-object-read-models-v2`
2. requires exact one-to-one agreement between discovered reviewed objects and
   catalog rows marked `reviewed_corpus`
3. rejects duplicate reviewed ids on either side
4. chooses the latest parseable object `observed_at`, intake `created_at`, or
   receipt `landed_at`, and fails when none exists
5. validates the canonical four generated-from refs, count, and timestamp
6. produces the derived summary without mutating any input

The adapter owns the inverse concerns: exact path roots, deterministic file
discovery, JSON object loading, logical-ref translation, and immutable bundle
construction.

The root `scripts/build_views.py` facade resolves `AOA_MEMO_ROOT` or the normal
neighbor root, exposes compatibility source/build functions, and delegates to
the adapter and core. It does not duplicate their rules. This keeps existing
build and publication callers stable while moving mechanics logic into its
importable owner modules.

## Output

The summary publishes:

- `source_kind_counts`
- reviewed corpus counts by kind, review state, recall status, temperature, and
  KAG-lift status
- compact reviewed object refs
- reviewed-intake packet and landing receipt counts
- consumer handoff refs for `aoa-evals`, `aoa-kag`, `aoa-stats`,
  `aoa-playbooks`, and `aoa-agents`

## Authority

This is a derived movement summary only.

It may help consumers see whether reviewed memory is growing and where handoff
pressure exists. It does not decide memory truth, promote objects, land reviewed
intake, approve KAG facts, or replace `aoa-memo` source refs and receipts.

## Reference-only posture

Cycle 9 classified the earlier live admission as false-live. The classification
does not demote the owner corpus: these are real reviewed `aoa-memo` source
surfaces, not examples. The missing half is observation.

The automatic stats refresh watches the memo writeback JSONL publisher, but
that log is not guaranteed to change atomically with the memory catalog,
reviewed object bundles, reviewed-intake packets, and landing receipts. A
corpus change could therefore leave a previously advertised local summary
stale. Buildability at manual refresh time is not enough to advertise
continuous currentness.

Consequently:

- the committed summary and public schema remain available
- `live_state_capable` stays `false`
- live refresh omits the surface from its live-only catalog
- stale `state/generated/memory_movement_summary.min.json` copies are removed

## Activation condition

Future live activation requires a tested owner signal or watcher contract that
causes refresh whenever movement relevant to all four roots occurs. The same
bounded activation slice must prove source observation, regenerated output,
live-catalog parity, and stale cleanup before changing the authored selector
to `true`.

Merely adding more path fallbacks, resolving the corpus on demand, or relying
on unrelated receipt traffic does not satisfy this condition. See
`docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md` for
the durable rationale.

## Memory Consumer Boundary

`aoa-stats` is a route-only/read-only memory consumer for this surface. It may
publish reviewed object ids, provenance-bearing object refs, lifecycle and
recall posture, generated read-model counts, reviewed-intake packet counts, and
landing receipt counts.

It does not create local memo candidates, prepare reviewed-intake exports, run
landing plans as authority, or land durable memory.

Session evidence remains `.aoa` evidence until a reviewed owner route promotes
it through `aoa-memo` reviewed intake. `aoa_memo` MCP
brief/search/status/validation/landing-plan dry-runs are access-plane evidence
for review, not stats truth. Durable memory still lands as a reviewed source
patch in `aoa-memo`.

## Validate

Use the part-owned [`VALIDATION.md`](../VALIDATION.md).
