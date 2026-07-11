# Contract

## Authority

- `aoa-memo` owns reviewed memory objects, intake, recall, and landing truth.
- `aoa-stats` may publish a descriptive movement read model only.
- `.aoa` session evidence remains session evidence until reviewed intake.
- No local memo candidate or write path is created here.

## Source boundary

The source adapter reads exactly these four `aoa-memo` roots, with no example,
fixture, history, or alternate-path fallback:

1. `generated/memory-objects/memory_object_catalog.min.json`
2. `memo/objects/**/object.json`
3. `memo/intake/reviewed/*.json`
4. `memo/intake/receipts/*.json`

Discovery is deterministic: reviewed objects use sorted recursive
`object.json` discovery, while reviewed-intake packets and landing receipts use
sorted direct JSON discovery. The adapter returns a deeply immutable input
bundle carrying logical repo refs rather than leaking local paths into the
projection core.

## Projection boundary

- `src/aoa_stats_builder/memory_movement.py` is the filesystem-free core. It
  has no `Path`, environment, or JSON I/O responsibility.
- The core requires exact agreement between reviewed corpus object ids and the
  catalog's `reviewed_corpus` ids, rejects duplicates, and refuses a bundle
  with no observable object, intake, or landing timestamp.
- `src/aoa_stats_builder/memory_movement_sources.py` owns path resolution,
  deterministic discovery, JSON loading, logical ref adaptation, and frozen
  bundle construction.
- `scripts/build_views.py` retains root compatibility names, neighbor/env root
  selection, CLI orchestration, and output fan-out. It delegates source loading
  and projection and does not own a second implementation.
- The committed JSON bytes, public schema, authority ceiling, and consumer
  handoff remain unchanged by this split.

## Live posture

The active profile is reference-only with `live_state_capable: false`.
Cycle 9 found a false-live admission, not a false owner source: the four roots
are real reviewed `aoa-memo` truth, but the installed refresh path does not
observe their movement. The memo writeback receipt log is not an atomic signal
for catalog, object, reviewed-intake, and landing changes.

Live refresh must omit Memory Movement from its catalog and remove any stale
runtime copy. Manual or committed builds may still resolve the exact owner
snapshot through the adapter.

## Activation condition

Live admission may return only when one bounded change provides a tested owner
signal or watcher contract that causes refresh for movement across the entire
four-root source contract, proves refreshed output/catalog parity and stale
cleanup, and changes the authored profile deliberately. Readability on demand
or a root compatibility facade is not an observation route.

The durable rationale is recorded in
`docs/decisions/AOST-D-0004-live-admission-requires-refresh-observation.md`.
