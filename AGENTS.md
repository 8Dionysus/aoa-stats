# AGENTS.md

Root route card for `aoa-stats`.

## Purpose

`aoa-stats` is the derived observability layer for AoA.
It consumes source-owned receipts, evidence refs, and bounded eval verdicts to produce machine-readable summaries that help the project read movement without stealing meaning from owner repositories.
Dashboards are lanterns, not sovereigns.

## Owner lane

This repository owns:

- derived summary schemas, shared receipt envelope, and event-kind vocabulary consumed by stats builders
- deterministic builders and validators for stats read models
- generated machine-first summary surfaces and stats boundary docs
- repo-local MCP surfaces when they remain derived-only

It does not own:

- workflow, proof, practice, scenario, role, memory, runtime, route, quest-state, or self-agent truth
- mastery, intent, or current truth inferred from volume alone

## Start here

1. `README.md`
2. `ROADMAP.md`
3. `docs/BOUNDARIES.md`
4. `docs/ARCHITECTURE.md`
5. `docs/LIVE_SESSION_USE.md`
6. `docs/COMPONENT_REFRESH_SUMMARIES.md` for derived-only component refresh summary posture
7. the schema, builder, receipt source, generated surface, or MCP surface you plan to touch
8. `docs/AGENTS_ROOT_REFERENCE.md` for preserved full root branches


## AGENTS stack law

- Start with this root card, then follow the nearest nested `AGENTS.md` for every touched path.
- Root guidance owns repository identity, owner boundaries, route choice, and the shortest honest verification path.
- Nested guidance owns local contracts, local risk, exact files, and local checks.
- Authored source surfaces own meaning. Generated, exported, compact, derived, runtime, and adapter surfaces summarize, transport, or support meaning.
- Self-agency, recurrence, quest, progression, checkpoint, or growth language must stay bounded, reviewable, evidence-linked, and reversible.
- Report what changed, what was verified, what was not verified, and where the next agent should resume.

## Derived-only rules

- Counts, windows, and movement summaries stay weaker than owner-local proof and source surfaces.
- `aoa_stats` MCP context starts with catalog or preview and never becomes route, proof, write, or quest-state authority.
- Keep evidence refs instead of duplicating raw artifacts when possible.

## Verify

Minimum validation:

```bash
python scripts/build_views.py --check
python scripts/validate_repo.py
python -m pytest -q tests
```

When refresh behavior, watchers, or owner-local receipt intake change:

```bash
python scripts/check_live_publishers.py
python scripts/refresh_live_stats.py
```

## Report

State which derived surface changed, whether output shape or receipt registration changed, which owner repos supplied facts, and what validation ran.

## Full reference

`docs/AGENTS_ROOT_REFERENCE.md` preserves the former detailed root guidance, including branch docs for stress summaries, growth funnels, live refresh, MCP posture, and release hygiene.
