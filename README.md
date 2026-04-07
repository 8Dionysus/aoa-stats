# aoa-stats

Derived observability and machine-first summary layer for the AoA federation.

`aoa-stats` is the downstream adjunct that consumes source-owned receipts,
evidence refs, and bounded eval verdicts to build machine-readable summaries
without taking ownership away from `aoa-skills`, `aoa-evals`, `aoa-playbooks`,
`aoa-techniques`, `aoa-agents`, `aoa-memo`, or `abyss-stack`.

This repository exists so project growth can stay visible during real work and
real sessions while preserving the canonical split:

- owner repos say what happened and what it means
- `aoa-stats` derives how often, how broadly, and how movement looks across
  named windows and pipelines
- project-core kernel usage is read from its own summary surface rather than
  inferred from total receipt volume

## Start here

Use the shortest route by need:

- ownership and anti-collapse rule: `docs/BOUNDARIES.md`
- five-layer architecture and derived posture: `docs/ARCHITECTURE.md`
- live receipt intake and generation loop: `docs/LIVE_SESSION_USE.md`
- local agent instructions: `AGENTS.md`

## Route by need

- current derived schemas: `schemas/`
- first-wave derived antifragility vector doctrine and contract:
  `docs/ANTIFRAGILITY_VECTOR.md`,
  `schemas/antifragility_vector_v1.json`, and
  `examples/antifragility_vector.example.json`
- canonical shared receipt envelope and active event family:
  `schemas/stats-event-envelope.schema.json`
- example receipt feed: `examples/session_harvest_family.receipts.example.json`
- canonical live source registry for owner-local receipts:
  `config/live_receipt_sources.json`
- example live source registry for bounded docs/testing:
  `config/live_receipt_sources.example.json`
- generated summary surfaces: `generated/`
- builders and validators: `scripts/build_views.py`,
  `scripts/refresh_live_stats.py`,
  `scripts/check_live_publishers.py`,
  `scripts/install_live_refresh_units.py`, and
  `scripts/validate_repo.py`
- local verification path: `python scripts/build_views.py --check`,
  `python scripts/validate_repo.py`, and `python -m pytest -q tests`

## What `aoa-stats` owns

This repository is the source of truth for:

- derived summary schemas for cross-repo stats read models
- the canonical shared receipt envelope and cross-repo event-kind vocabulary
  consumed by stats builders
- machine-first generated summary surfaces built from source-owned receipts
- deterministic builders and validators for derived views
- docs that define how counts, verdicts, progression, and evidence stay
  separated at the stats layer

## What it does not own

- It does not own workflow meaning from `aoa-skills`.
- It does not own proof meaning or verdict interpretation from `aoa-evals`.
- It does not own scenario composition from `aoa-playbooks`.
- It does not own role or checkpoint contracts from `aoa-agents`.
- It does not own memory or provenance-thread meaning from `aoa-memo`.
- It does not own runtime execution or closeout meaning from `abyss-stack`.
- It does not become a sovereign score empire or dashboard authority.

## Core rule

Source repos own meaning. `aoa-stats` owns derived views.

If a stats surface starts behaving like workflow authority, proof authority, or
quest-state authority, the layer is drifting out of bounds.

## Current v0 surface

The first usable derived summaries are:

- `generated/object_summary.min.json`
- `generated/core_skill_application_summary.min.json`
- `generated/repeated_window_summary.min.json`
- `generated/route_progression_summary.min.json`
- `generated/fork_calibration_summary.min.json`
- `generated/automation_pipeline_summary.min.json`
- `generated/runtime_closeout_summary.min.json`
- `generated/surface_detection_summary.min.json`
- `generated/summary_surface_catalog.min.json`

These are built from one bounded receipt feed and are intended to stay
machine-first, evidence-linked, and weaker than the owner-local source
surfaces they summarize.

`surface_detection_summary.min.json` is second-wave descriptive only. It may
count shortlist ambiguity, candidate posture, and closeout-handoff volume when
owner receipts preserve that context, but it does not decide promotion or
owner meaning.

Raw logs stay append-only. When receipts carry `supersedes`, the committed and
live summaries read from the active receipt view after local correction
collapse, not from raw line volume.

For real local session work, keep the committed `generated/` surfaces stable
and refresh ephemeral live state under `state/`.

## Verify current repo state

```bash
python scripts/build_views.py --check
python scripts/validate_repo.py
python -m pytest -q tests
```

## Local build

Refresh the derived surfaces from one or more receipt feeds:

```bash
python scripts/build_views.py \
  --input examples/session_harvest_family.receipts.example.json \
  --output-dir generated
```

Refresh the local live state from owner-local source feeds under `/srv`:

```bash
python scripts/refresh_live_stats.py
```

Audit all required live publishers before or after a refresh:

```bash
python scripts/check_live_publishers.py
```

Install the user-level watcher so live summaries refresh automatically whenever
an owner-local receipt log changes:

```bash
python scripts/install_live_refresh_units.py --enable
```

The canonical watcher currently listens to these owner-local logs:

- `/srv/aoa-skills/.aoa/live_receipts/session-harvest-family.jsonl`
- `/srv/aoa-skills/.aoa/live_receipts/core-skill-applications.jsonl`
- `/srv/aoa-evals/.aoa/live_receipts/eval-result-receipts.jsonl`
- `/srv/aoa-playbooks/.aoa/live_receipts/playbook-receipts.jsonl`
- `/srv/aoa-techniques/.aoa/live_receipts/technique-receipts.jsonl`
- `/srv/aoa-memo/.aoa/live_receipts/memo-writeback-receipts.jsonl`
- `/srv/abyss-stack/.aoa/live_receipts/runtime-wave-closeouts.jsonl`

## Go elsewhere when...

- you need the workflow that emitted the receipt: `aoa-skills`
- you need proof meaning or eval verdict interpretation: `aoa-evals`
- you need reusable practice meaning: `aoa-techniques`
- you need scenario composition: `aoa-playbooks`
- you need role or checkpoint meaning: `aoa-agents`
- you need memory or provenance ownership: `aoa-memo`
- you need runtime-local trial or closeout truth: `abyss-stack`

## License

Apache-2.0
