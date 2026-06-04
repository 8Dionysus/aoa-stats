# AOST-D-0002 Canonical Decision Lane

## Index Metadata

- Decision ID: AOST-D-0002
- Original date: 2026-06-04
- Surface classes: docs/decisions, scripts/validators, tests/release-checks, docs/routes
- Stats surfaces: decision lane, generated lookup indexes, derived-only boundary
- Source lanes: aoa-stats, sibling decision-lane pattern
- Guard families: generated-index parity, derived-only authority, route-law validation
- Posture: accepted

## Status

Accepted

## Context

`aoa-stats` had a real decision note, but it still lived as a date-slug file
with no generated lookup indexes. That made the rationale harder to address
from other route surfaces and weaker than the emerging sibling-repo pattern for
durable decision lanes.

The stats repository also has a sharper authority ceiling than many siblings:
it owns derived observability, not source meaning, proof verdicts, workflow
truth, route truth, or memory truth. A copied decision lane would be too broad
unless it named that derived-only boundary as the center of the contract.

## Decision

`docs/decisions/` now uses stable `AOST-D-####-short-slug.md` filenames, an
`## Index Metadata` block in every decision note, generated lookup indexes under
`docs/decisions/indexes/`, and validation through
`scripts/generate_decision_indexes.py` plus
`scripts/validate_decision_records.py`.

The lane records why `aoa-stats` chose a derived-observability route. It does
not become a live dashboard, a proof source, a route dispatcher, a memory
promotion ledger, or a replacement for the source-owned receipts and verdicts
that stats summarizes.

## Options Considered

- Keep the date-slug file only: preserved the old note, but left addressing and
  route lookup weaker than sibling repositories.
- Copy a sibling lane verbatim: gave symmetry, but risked importing KAG,
  routing, or public-entry language that does not belong to derived stats.
- Use the sibling generated-index shape with `aoa-stats` metadata: keeps the
  durable contract symmetrical while letting the stats boundary remain local.

## Rationale

`AOST` is the local namespace already visible in repo quest surfaces, so
`AOST-D` is the least surprising decision prefix. Generated indexes give agents
cheap lookup by number, date, surface class, stats surface, source lane, and
guard family without turning `README.md` into a drifting roster.

The metadata deliberately names stats surfaces and source lanes because the
future risk is overreading derived counts as owner truth. A decision note can
explain why stats summarized a surface, but owner repositories still decide
what their receipts, proof, routes, roles, memory objects, and source meaning
actually mean.

## Consequences

- Future material stats-boundary decisions get stable IDs and generated lookup.
- Decision indexes are read models only and must be regenerated, not edited by
  hand.
- Historical date-slug paths belong to git history, not to a compatibility
  alias layer.
- Changes to accepted rationale should usually add a new decision with explicit
  supersession prose instead of silently rewriting the old route.

## Source Surfaces

- `AGENTS.md`
- `README.md`
- `ROADMAP.md`
- `docs/BOUNDARIES.md`
- `docs/ARCHITECTURE.md`
- `docs/README.md`
- `docs/decisions/AGENTS.md`

## Validation

Run:

```bash
python scripts/generate_decision_indexes.py
python scripts/generate_decision_indexes.py --check
python scripts/validate_decision_records.py
python scripts/validate_nested_agents.py
python scripts/validate_repo.py
python -m pytest -q tests
```
