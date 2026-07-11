# AGENTS.md

Route card for authored stats read-model profiles.

## Ownership

`stats/read-models/` owns the source-authored surface profiles that say what a
derived summary asks, which public schema and output carry it, which stronger
owners remain authoritative, and which mechanics produce or refresh it.

It does not own Python implementation, generated output, mechanic payloads,
or the upstream facts summarized by a profile.

## Read before editing

1. `../AGENTS.md`
2. `README.md`
3. `surface-profile.schema.json`
4. the target profile under `active/` or `deferred/`
5. every schema, output, and mechanic route named by that profile

## Profile law

- One active public catalog surface has one authored profile under `active/`.
- Contract-only candidates live under `deferred/` until their activation
  condition and evidence chain are real.
- Preserve `catalog_order`; it is the deterministic public catalog order.
- `mechanic_routes` are source-to-operation handoffs. They do not move source
  meaning into mechanics.
- `live_state_capable` is executable source meaning: `true` admits the surface
  to local live materialization, while `false` keeps it on its committed or
  reference route and out of the live catalog.
- Do not add Python, generated catalogs, live receipts, or copied owner
  payloads here.
- Change the authored profile first, then rebuild and check the generated
  catalog.
- For Route Progression, return progression-reading vocabulary to the RPG
  center, receipt payloads to `aoa-skills`, the agent-layer overlay to
  `aoa-agents`, and typed transport to `aoa-sdk`. The committed legacy numeric
  snapshot stays non-live while the current owner receipt is semantic and
  non-score-shaped; the profile must not manufacture a numeric mapping.

## Verification

```bash
python scripts/validate_stats_source_home.py
python scripts/build_views.py --check
python -m pytest -q tests/test_stats_source_home.py tests/test_summary_surface_catalog.py
```
