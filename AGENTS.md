# AGENTS.md

Guidance for coding agents and humans contributing to `aoa-stats`.

## Purpose

`aoa-stats` is the derived observability layer for AoA.
It consumes source-owned receipts, evidence refs, and bounded eval verdicts to
produce machine-readable summaries that help the project read movement during
work and sessions without stealing meaning from owner repositories.

This layer exists so growth can stay visible without turning dashboards into
sovereigns.

## Owns

This repository is the source of truth for:

- derived summary schemas
- the shared receipt envelope and event-kind vocabulary consumed by stats builders
- deterministic builders and validators for stats read models
- generated machine-first summary surfaces
- docs that define the stats-layer boundary and anti-collapse rules

## Does not own

Do not treat this repository as the source of truth for:

- workflow meaning in `aoa-skills`
- proof meaning or verdict interpretation in `aoa-evals`
- practice meaning in `aoa-techniques`
- scenario composition or questline posture in `aoa-playbooks`
- role, progression, or checkpoint meaning in `aoa-agents`
- memory or provenance-thread meaning in `aoa-memo`
- runtime execution or closeout meaning in `abyss-stack`
- live quest state, live route authority, or self-agent proof

## Core rules

Keep stats derived.

This layer may summarize counts, windows, and movement.
It must not replace bounded proof, workflow meaning, or route-state authority.

A stats surface may illuminate change.
It does not by itself prove mastery, intent, or self-agency.

## Read this first

Before making changes, read in this order:

1. `README.md`
2. `docs/BOUNDARIES.md`
3. `docs/ARCHITECTURE.md`
4. `docs/LIVE_SESSION_USE.md`
5. the schema, builder, or generated surface you plan to touch

Then branch by task:

- stress recovery or derived signal hygiene:
  `docs/STRESS_RECOVERY_WINDOW_SUMMARIES.md` and
  `docs/DERIVED_SIGNAL_HYGIENE.md`
- receipt envelope or source-registry changes:
  `schemas/stats-event-envelope.schema.json`,
  `config/live_receipt_sources.json`, and
  `config/live_receipt_sources.example.json`
- live refresh or watcher behavior:
  `scripts/refresh_live_stats.py`,
  `scripts/check_live_publishers.py`, and
  `scripts/install_live_refresh_units.py`
- release prep or public repo hygiene:
  `docs/RELEASING.md`,
  `CHANGELOG.md`,
  `SECURITY.md`,
  `CONTRIBUTING.md`, and
  `CODE_OF_CONDUCT.md`

If a deeper directory defines its own `AGENTS.md`, follow the nearest one.

## Primary objects

The most important objects in this repository are:

- `schemas/*.json`
- `schemas/stats-event-envelope.schema.json`
- `generated/*.json`
- `CHANGELOG.md`
- `docs/RELEASING.md`
- `config/live_receipt_sources*.json`
- `scripts/build_views.py`
- `scripts/check_live_publishers.py`
- `scripts/refresh_live_stats.py`
- `scripts/install_live_refresh_units.py`
- `scripts/validate_repo.py`
- example receipt feeds under `examples/`
- tests that prove derivation and boundary integrity

## Hard NO

Do not:

- let one summary surface pretend to be proof authority
- turn counts into a universal score
- duplicate raw artifacts when evidence refs are enough
- move workflow, proof, or role ownership into this repo
- let route progression or stress summaries become live quest authority
- infer self-agency or current truth from receipt volume alone
- quietly widen this repo into a dashboard monolith

## Contribution doctrine

Use this flow: `PLAN -> DIFF -> VERIFY -> REPORT`

### PLAN

State:

- which derived surface, schema, or builder is changing
- which owner repos supply the input facts
- whether output shape changes
- whether live receipt source registration changes
- what authority-drift risk exists

### DIFF

Keep the change focused.
Prefer deterministic derivation over hidden heuristics.
Do not mix unrelated cleanup into a stats change unless it is necessary for
repository integrity.

### VERIFY

Minimum validation:

```bash
python scripts/build_views.py --check
python scripts/validate_repo.py
python -m pytest -q tests
```

Use the live-loop verification path when the task touches refresh behavior,
watchers, or owner-local receipt intake:

```bash
python scripts/check_live_publishers.py
python scripts/refresh_live_stats.py
```

Confirm that:

- source ownership is still preserved
- generated outputs remain deterministic
- summaries stay machine-first, evidence-linked, and weaker than owner-local source surfaces
- progression, stress, route, or closeout summaries remain descriptive rather than authoritative
- no stats surface quietly becomes workflow, proof, or quest-state truth

### REPORT

Summarize:

- what changed
- which derived surfaces changed
- whether output shape changed
- which owner repos were involved
- what validation you actually ran
- any remaining boundary or rollout caveats

## Validation

Do not claim checks you did not run.
