# AGENTS.md

Guidance for coding agents and humans contributing to `aoa-stats`.

## Purpose

`aoa-stats` is the derived observability layer for AoA. It consumes
source-owned receipts, evidence refs, and bounded eval verdicts to produce
machine-readable summaries that help the project read movement during work and
sessions without stealing meaning from owner repositories.

## Owns

This repository is the source of truth for:

- derived summary schemas
- deterministic builders and validators for stats read models
- generated machine-first summary surfaces
- docs that define the stats-layer boundary and anti-collapse rules

## Does not own

Do not treat this repository as the source of truth for:

- workflow meaning in `aoa-skills`
- proof meaning in `aoa-evals`
- practice meaning in `aoa-techniques`
- scenario composition in `aoa-playbooks`
- role or checkpoint meaning in `aoa-agents`
- memory or provenance-thread meaning in `aoa-memo`

## Core rule

Keep stats derived.

This layer may summarize counts, windows, and movement. It must not replace
bounded proof, workflow meaning, or route-state authority.

## Read this first

Before making changes, read in this order:

1. `README.md`
2. `docs/BOUNDARIES.md`
3. `docs/ARCHITECTURE.md`
4. `docs/LIVE_SESSION_USE.md`
5. the schema, builder, or generated surface you plan to touch

If a deeper directory defines its own `AGENTS.md`, follow the nearest one.

## Primary objects

The most important objects in this repository are:

- `schemas/*.json`
- `generated/*.json`
- `scripts/build_views.py`
- `scripts/validate_repo.py`
- `examples/session_harvest_family.receipts.example.json`
- tests that prove derivation and boundary integrity

## Hard NO

Do not:

- let one summary surface pretend to be proof authority
- turn counts into a universal score
- duplicate raw artifacts when evidence refs are enough
- move workflow or proof ownership into this repo
- quietly widen this repo into a dashboard monolith

## Contribution doctrine

Use this flow: `PLAN -> DIFF -> VERIFY -> REPORT`

### PLAN

State:

- which derived surface or builder is changing
- which owner repos supply the input facts
- whether output shape changes
- what authority-drift risk exists

### DIFF

Keep the change focused. Prefer deterministic derivation over hidden heuristics.

### VERIFY

Minimum validation:

```bash
python scripts/build_views.py --check
python scripts/validate_repo.py
python -m pytest -q tests
```

### REPORT

Summarize:

- what changed
- which derived surfaces changed
- whether output shape changed
- what validation you actually ran
- any remaining boundary or rollout caveats

## Validation

Do not claim checks you did not run.

