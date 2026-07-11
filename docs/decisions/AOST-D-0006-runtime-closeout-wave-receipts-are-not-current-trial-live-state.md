# AOST-D-0006 Runtime Closeout Wave Receipts Are Not Current Trial Live State

## Index Metadata

- Decision ID: AOST-D-0006
- Original date: 2026-07-11
- Surface classes: stats/read-models, mechanics/checkpoint, mechanics/recurrence, src/projection, state/generated, config/registry
- Stats surfaces: Runtime Closeout, live summary catalog, live receipt source registry, Source Coverage
- Source lanes: abyss-stack runtime trial closeouts, Agents-of-Abyss checkpoint center, aoa-sdk reviewed closeout transport
- Guard families: derived-only authority, live-source admission, owner-contract compatibility, refresh observation, schema-output parity, stale-output cleanup, source coverage
- Posture: accepted

## Status

Accepted

## Context

The committed Runtime Closeout summary accepts the historical
`runtime_wave_closeout_receipt` shape and groups it by `program_id` and
`wave_id`. That receipt family was introduced by `abyss-stack` commit
`27b8035`, and one historical wave receipt remains in the bounded aoa-stats
fixture and public output.

The current tracked `abyss-stack` local-trials producer at `f41621e` instead
emits `runtime_trial_closeout_receipt` to
`.aoa/live_receipts/runtime-trial-closeouts.jsonl`. The current `aoa-sdk`
Checkpoint transport separately emits `runtime_return_closeout_receipt`; its
`build_runtime_wave_closeout_receipt` compatibility name delegates to that
return contract rather than recreating the historical stats wave payload.

Before this decision the Runtime Closeout profile still claimed
`receipt_backed_live`, and the active source registry watched the old
`runtime-wave-closeouts.jsonl` path. At the 2026-07-11 audit, the host had one
stale receipt in that old log, while no current trial log had yet been
observed. Merely switching the profile to false would hide the Runtime Closeout
output but would still admit the stale wave receipt into Object, Repeated
Window, and Source Coverage live summaries.

At the 2026-07-11 audit, the installed user units were symlinks into an
abyss-stack-owned deploy snapshot, named the old path, and launched an older
`/srv/AbyssOS/aoa-stats` projection whose registry admitted that source. The
repo-local change therefore did not repair or certify the installed plane.
Running the repo installer with overwrite from an ephemeral checkout would
follow the symlink and mutate the owner-owned target while embedding the wrong
checkout path, so deployment requires a separate symlink-safe owner handoff.

## Decision

Runtime Closeout remains an active committed compatibility surface but becomes
reference-only. Its deterministic core moves to
`src/aoa_stats_builder/runtime_closeout.py`, while `scripts/build_views.py`
retains exact compatibility aliases and repo-wide fan-out. The public schema,
fixture, generated path, payload bytes, and historical event-kind admission
remain stable.

The active live-source registry removes the historical abyss-stack wave log.
Live refresh therefore neither reads that receipt nor invokes, materializes,
or catalogs Runtime Closeout; cleanup removes any stale managed runtime copy.

`runtime_wave_closeout_receipt`, `runtime_trial_closeout_receipt`, and
`runtime_return_closeout_receipt` are distinct contracts. aoa-stats does not
rename, merge, or infer an adapter among them. Future live activation requires:

1. an explicit cross-owner agreement naming one canonical receipt ABI;
2. a real current owner-local receipt conforming to that ABI;
3. stats envelope and event-kind registration when a new kind is selected;
4. active source-registry and watcher parity for the real log;
5. end-to-end publisher, refresh, schema, catalog, and stale-cleanup proof.

## Options Considered

- Keep the old wave source live and map trial or return receipts into it:
  rejected because the payload owners have not declared those contracts
  equivalent.
- Set the old registry source to `required: false`: rejected because an
  existing stale file would still be read and contaminate unrelated live
  summaries.
- Add a new `active: false` registry protocol: rejected for this cycle because
  refresh, publisher audit, watcher installation, and Source Coverage would
  all need a new shared state machine while the honest active-owner baseline
  would still exclude abyss-stack.
- Remove Runtime Closeout entirely: rejected because its historical committed
  snapshot and stable public contract remain useful.
- Retain the committed surface, remove the stale live source, and require an
  owner-approved reactivation: chosen because it preserves compatibility
  without advertising historical data as current runtime truth.

## Rationale

Checkpoint vocabulary and authority stop-lines belong to the
`Agents-of-Abyss` center. Runtime execution, gates, and trial publication
belong to `abyss-stack`. Reviewed closeout transport belongs to `aoa-sdk`.
aoa-stats may publish a weaker deterministic view only when the receipt it
projects is explicitly admitted and observed; it may not manufacture ABI
equivalence from similar names.

Separating compatibility admission from live-source admission keeps both
truths visible: the old fixture remains reproducible, while the local live
plane stops treating an April wave receipt as current owner state. Removing
the source rather than only the surface also prevents quiet cross-summary
contamination.

## Consequences

- The managed inventory remains 25 active profiles; 11 are live-admitted and
  14 are committed/reference-only.
- `generated/runtime_closeout_summary.min.json` retains its existing schema,
  bytes, and SHA-256
  `2f3b958e75099e8ae0a3035eca60be7b8809cf2f6950fdfaa2f934ab1845649c`.
- Runtime Closeout is omitted from the live output and catalog, its builder is
  not invoked there, and stale runtime copies are cleaned.
- The canonical live-source registry contains six sources rather than seven
  and no longer reads `runtime-wave-closeouts.jsonl`.
- Source Coverage derives five expected owner repos rather than six. In the
  committed fixture `abyss-stack` is now honestly unexpected alongside
  `Dionysus`, because its receipt is historical relative to the current live
  registry.
- At decision time, the installed watcher and service remained on the old
  deploy projection and could still admit the old feed. This repository
  landing proves only the current source contract and an isolated refresh; a
  separate abyss-stack/deploy migration must be verified before the live host
  plane can be claimed fixed.
- A current trial or return receipt remains unsupported until the owner
  reactivation conditions are satisfied.

## Source Surfaces

- `stats/read-models/active/runtime_closeout_summary.profile.json`
- `stats/intake-contract/event-kind-registry.json`
- `stats/intake-contract/examples/session_harvest_family.receipts.example.json`
- `stats/source_home.manifest.json`
- `src/aoa_stats_builder/runtime_closeout.py`
- `schemas/runtime-closeout-summary.schema.json`
- `generated/runtime_closeout_summary.min.json`
- `scripts/build_views.py`
- `mechanics/checkpoint/parts/runtime-closeout/`
- `mechanics/recurrence/parts/live-receipt-refresh/config/live_receipt_sources.json`
- `mechanics/recurrence/parts/live-receipt-refresh/scripts/refresh_live_stats.py`
- `mechanics/recurrence/parts/live-receipt-refresh/scripts/install_live_refresh_units.py`
- `mechanics/recurrence/parts/live-receipt-refresh/systemd/aoa-stats-live-refresh.path`
- `mechanics/recurrence/parts/live-receipt-refresh/systemd/aoa-stats-live-refresh.service`
- `mechanics/recurrence/parts/live-receipt-refresh/tests/test_refresh_live_stats.py`
- `abyss-stack/mechanics/inference-pilots/parts/local-trials/compatibility-runners/aoa-local-ai-trials`
- `abyss-stack/systemd/user/aoa-stats-live-refresh.path`
- `abyss-stack/systemd/user/aoa-stats-live-refresh.service`
- `Agents-of-Abyss/mechanics/checkpoint/README.md`
- `aoa-sdk/src/aoa_sdk/a2a/rebase/closeout.py`

## Validation

Run:

```bash
python scripts/generate_decision_indexes.py
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
python scripts/validate_stats_source_home.py
python scripts/validate_mechanics_topology.py
python scripts/build_views.py --check
python -m pytest -q mechanics/checkpoint/parts/runtime-closeout/tests mechanics/recurrence/parts/live-receipt-refresh/tests tests/test_build_views.py tests/test_summary_surface_catalog.py
python scripts/release_check.py
```
